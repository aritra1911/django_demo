import json
from tqdm import tqdm
from django.core.management.base import BaseCommand
from django.db.models import Model
from django.db.utils import IntegrityError
from kbapp.models import AMCFund
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
        updated: int = 0

        self.stdout.write('Preparing to insert data into AMCFund')
        pbar: tqdm = tqdm(ascii=False, desc='Inserting Funds', total=num_funds)
        for fund_data in master_data['funds']:
            field_data: Dict[str, str] = {
                'fund_category': fund_data['category'],
                'fund_type': fund_data['category'],
                'name': fund_data['schdesc'],
                'risk_factor': fund_data['risktype'],
                'fund_sub_type': fund_data['subcategory'],
                'rta_fund_code': fund_data['scheme'],
            }

            fund: Optional[AMCFund] = AMCFund.update_by_rta_fund_code(
                **field_data
            )
            if not fund:    # got created, i.e. it got updated
                updated += 1

            pbar.update(1)

        pbar.close()
        self.stdout.write('----------------------')
        self.stdout.write(
            msg=f'inserted : { num_funds - updated }\nupdated : { updated }',
            style_func=self.style.SUCCESS
        )
