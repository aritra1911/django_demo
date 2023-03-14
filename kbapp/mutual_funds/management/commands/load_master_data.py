import json
import datetime
from tqdm import tqdm
from django.core.management.base import BaseCommand
from django.db.models import Model
from django.db.utils import IntegrityError
from kbapp.models import AMCFund, AMCScheme
from kbapp.mutual_funds.management.commands._mappers import fund_mapper, scheme_mapper
from typing import Dict, Optional, Any


class Command(BaseCommand):
    help = 'Inserts master data from a JSON file into the AMCFund table'

    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str, help='Path to the master data JSON file.')

    def handle(self, *args, **options) -> None:
        json_file: str = options['json_file']
        master_data: Dict[str, Any]

        # Read data from the specified file 
        self.stdout.write(f'Reading data from { json_file }')
        try:
            with open(json_file, 'r') as f:
                master_data = json.load(f)
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"An error occurred while trying to read { json_file }: { str(e) }"))
            return
        self.insert_master_data(master_data['data'])

    def insert_master_data(self, master_data: Any) -> None:
        num_funds: int = len(master_data['funds'])
        num_schemes: int = sum([ len(fund['schemes']) for fund in master_data['funds'] ])
        created: bool
        funds_updated: int = 0
        schemes_updated: int = 0

        self.stdout.write('Preparing to insert data into AMCFund')
        pbar: tqdm = tqdm(ascii=False, desc='Inserting or updating from master data', total=num_schemes)

        for fund_data in master_data['funds']:
            fund_payload: Dict[str, Any] = fund_mapper(fund_data)

            fund, created = AMCFund.create_or_update_by_rta_fund_code(**fund_payload)
            if not created:
                funds_updated += 1

            for scheme_data in fund_data['schemes']:
                scheme_payload: Dict[str, Any] = scheme_mapper(scheme_data, fund)

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
