import json
import datetime
from tqdm import tqdm
from django.core.management.base import BaseCommand
from django.db.models import Model
from django.db.utils import IntegrityError
from kbapp.models import AMCFund, AMCScheme
from typing import Dict, Optional, Any


def get_cutoff_time(param: int):
    if isinstance(param, int):
        str_time = str(param)
        if len(str_time) == 4:
            cutoff_time_hour = int(str_time[:2])
            cutoff_time_min = int(str_time[2:])
            cut_off_time = datetime.time(cutoff_time_hour, cutoff_time_min)
        else:
            cut_off_time = ''
    else:
        cut_off_time = ''
    return cut_off_time


class Command(BaseCommand):
    help = 'Inserts master data from a JSON file into the AMCFund table'

    def add_arguments(self, parser):
        parser.add_argument(
            'json_file',
            type=str,
            help='Path to the master data JSON file.'
        )

    def handle(self, *args, **options) -> None:
        # Get the JSON Data filename from the User
        json_file: str = options['json_file']

        # Read data from the specified file 
        self.stdout.write(f'Reading data from { json_file }')
        try:
            with open(json_file, 'r') as f:
                master_data = json.load(f)
        except Exception as e:
            self.stderr.write(self.style.ERROR(
                f"An error occurred while trying to read { json_file }: " +
                str(e)
            ))
            return
        return self.insert_master_data(master_data['data'])

    def insert_master_data(self, master_data: Any) -> None:
        num_funds: int = len(master_data['funds'])
        num_schemes: int = sum([ len(fund['schemes']) for fund in master_data['funds'] ])
        created: bool
        funds_updated: int = 0
        schemes_updated: int = 0

        self.stdout.write('Preparing to insert data into AMCFund')
        pbar: tqdm = tqdm(ascii=False, desc='Inserting or updating from master data', total=num_schemes)

        for fund in master_data['funds']:
            fund_payload = {
                'fund_type': fund['category'],
                'fund_sub_type': fund['subcategory'],
                'risk_factor': fund['risktype'],
                'rta_fund_code': fund['scheme'],
                'fund_category': fund['category'],
                #"modified_by": BATCH_USER,
            }

            fundobj, created = AMCFund.create_or_update_by_rta_fund_code(**fund_payload)
            if not created:
                funds_updated += 1

            for scheme in fund['schemes']:
                is_direct_fund: bool = 'direct' in scheme['plandesc'].lower()
                is_growth_fund: bool = 'growth' in scheme['plandesc'].lower()
                is_regular_fund: bool = 'regular' in scheme['plandesc'].lower()
                is_div_payout_fund: bool = 'payout' in scheme['optiondesc'].lower()
                is_div_reinvestment_fund: bool = 'reinvestment' in scheme['optiondesc'].lower()
                planoptiondesc = {
                    is_direct_fund and is_growth_fund: "Direct - Growth",
                    is_regular_fund and is_growth_fund: "Regular - Growth",
                    is_direct_fund and is_div_reinvestment_fund: "Direct – IDCW Reinvestment",
                    is_regular_fund and is_div_reinvestment_fund: "Regular – IDCW Reinvestment",
                    is_direct_fund and is_div_payout_fund: "Direct – IDCW Payout",
                    is_regular_fund and is_div_payout_fund: "Regular – IDCW Payout"
                }

                scheme_payload = {
                    "amcfund": fundobj,
                    "name": scheme['desc'],
                    "amfi_scheme_code": scheme['amficode'] if scheme['amficode'] else 0,
                    "is_active": scheme['active'] == 'Y',
                    "is_being_sold": scheme['purallow'] == 'Y',
                    "is_direct_fund": is_direct_fund,
                    "is_regular_fund": is_regular_fund,
                    "is_growth_fund": is_growth_fund,
                    "is_div_payout_fund": is_div_payout_fund,
                    "is_div_reinvestment_fund": is_div_reinvestment_fund,
                    "rta_scheme_planoptiondesc": planoptiondesc.get(True, ''),
                    "rta_scheme_option": scheme.get('optiondesc'),
                    "rta_sip_flag": scheme['sipallow'],
                    "rta_stp_flag": scheme['stpoallow'],
                    "rta_swp_flag": scheme['stpiallow'],
                    "rta_switch_flag": 'Y' if scheme['swiallow'] == 'Y' and scheme['swoallow'] == 'Y' else 'N',
                    "rta_stp_reg_in": scheme['stpiallow'],
                    "rta_stp_reg_out": scheme['stpoallow'],
                    "rta_scheme_code": scheme['schemeid'],
                    "rta_rta_scheme_code": scheme['schemeid'],
                    "rta_amc_scheme_code": scheme['schemeid'],
                    "rta_isin": scheme['isin'],
                    "rta_amc_code": scheme['fundname'],
                    "rta_scheme_type": fundobj.fund_category,
                    "rta_scheme_plan": scheme['plandesc'],
                    "rta_scheme_name": scheme['desc'],
                    "rta_scheme_active_flag": scheme['active'],
                    "rta_lock_in_period_flag": 'N',
                    "rta_lock_in_period": 0,
                    "rta_plan_code": scheme['plan'],
                    "rta_option_code": scheme['option'],
                    "is_nfo": scheme['nfoidentifier'],
                    "nfo_face_value": scheme['facevalue'],
                    "nfo_start_date": datetime.datetime.fromisoformat(scheme['opendate'][:-1] + '+00.00').date(),
                    "nfo_end_date": datetime.datetime.fromisoformat(scheme['closedate'][:-1] + '+00.00').date(),
                    "nfo_reopening_date": datetime.datetime.fromisoformat(scheme['reopendate'][:-1] + '+00.00').date(),

                    # Scheme Purchase Fields
                    "rta_purchase_allowed": scheme['purallow'],
                    "rta_minimum_purchase_amount": scheme['new_minamt'],
                    "rta_additional_purchase_amount_multiple": scheme['add_minamt'],
                    "rta_purchase_cutoff_time": get_cutoff_time(scheme['purcuttime']), # Convert to datetime.time

                    # Scheme Redeem Fields
                    "rta_redemption_allowed": scheme['redallow'],
                    "rta_redemption_amount_minimum": scheme['red_minamt'],
                    "rta_redemption_cutoff_time": get_cutoff_time(scheme['redcuttime']),  # Convert to datetime.time
                    #"modified_by": BATCH_USER,
                    "modified": datetime.datetime.now()
                }

                scheme, created = AMCScheme.create_or_update_by_name(**scheme_payload)
                if not created:
                    schemes_updated += 1

                pbar.update(1)

        pbar.close()
        self.stdout.write(
            msg=(
                f'----------------------\n'
                f'funds inserted : { num_funds - funds_updated }\n'
                f'funds updated : { funds_updated }\n'
                f'schemes inserted : { num_schemes - schemes_updated }\n'
                f'schemes updated : { schemes_updated }\n'
            ), style_func=self.style.SUCCESS
        )
