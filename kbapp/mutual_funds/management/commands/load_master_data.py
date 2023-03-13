import json
from tqdm import tqdm
from django.core.management.base import BaseCommand
from django.db.models import Model
from django.db.utils import IntegrityError
from kbapp.models import AMCFund, AMCScheme
from typing import Dict, Optional, Any


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
        num_schemes: int
        fund: AMCFund
        scheme: AMCScheme
        created: bool
        num_updated: int = 0

        self.stdout.write('Preparing to insert data into AMCFund')
        pbar: tqdm = tqdm(ascii=False, desc='Inserting Funds', total=num_funds)

        for fund_data in master_data['funds']:
            fund_field_data: Dict[str, str] = {
                'fund_category': fund_data['category'],
                'fund_type': fund_data['category'],
                'name': fund_data['schdesc'],
                'risk_factor': fund_data['risktype'],
                'fund_sub_type': fund_data['subcategory'],
                'rta_fund_code': fund_data['scheme'],
            }
            fund, created = AMCFund.create_or_update_by_rta_fund_code(**fund_field_data)
            if not created:
                num_updated += 1

            for scheme_data in fund_data['schemes']:
                scheme_field_data: Dict[str, Any] = {
                    'amcfund': fund,
                    'name': scheme_data['desc'],
                    #'amfi_scheme_code': scheme_data['amficode'],
                    #'isin_div_or_growth_code': scheme_data['isin'],
                    #'isin_div_reinvestment_code': scheme_data['isin'],
                    #'is_direct_fund': scheme_data['plan'],
                    #'is_div_payout_fund': scheme_data['optiondesc'],
                    #'is_active': scheme_data['active'],
                    #'rta_scheme_code': scheme_data['schemeid'],
                    #'rta_rta_scheme_code': scheme_data['schemeid'],
                    #'rta_amc_scheme_code': scheme_data['schemeid'],
                    #'rta_isin': scheme_data['isin'],
                    #'rta_amc_code': scheme_data['fundname'],
                    #'rta_scheme_type': scheme_data['category'],
                    #'rta_scheme_plan': scheme_data['plandesc'],
                    #'rta_scheme_name': scheme_data['desc'],
                    #'': scheme_data[''],
                    #'': scheme_data[''],
                    #'': scheme_data[''],
                    #'': scheme_data[''],
                    #'': scheme_data[''],
                    #'': scheme_data[''],
                    #'': scheme_data[''],
                    #'': scheme_data[''],
                    #'': scheme_data[''],
                    #'': scheme_data[''],
                }
                AMCScheme.create_or_update_by_name(**scheme_field_data)

            pbar.update(1)

        pbar.close()
        self.stdout.write('----------------------')
        self.stdout.write(
            msg=f'inserted : { num_funds - num_updated }\nupdated : { num_updated }',
            style_func=self.style.SUCCESS
        )
