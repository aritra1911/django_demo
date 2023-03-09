import json
from django.core.management.base import BaseCommand
from django.apps import apps
from django.db.models import Model
from django.db.utils import IntegrityError
from typing import Dict, Type


class Command(BaseCommand):
    help = 'Inserts data from a JSON file into the AMC table'

    def add_arguments(self, parser):
        parser.add_argument(
            'json_file',
            type=str,
            help='Path to the JSON file.'
        )

    def handle(self, *args, **options) -> None:
        # Get the JSON Data filename from the User
        json_file: str = options['json_file']
        return self.insert_data_from_json(json_file)

    def insert_data_from_json(self, json_file: str) -> None:
        # Read data from the specified file 
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
        except Exception as e:
            self.stderr.write(self.style.ERROR(
                f"An error occurred while trying to read { json_file }: " +
                str(e)
            ))
            return

        # Get the model from the JSON data
        try:
            model: Type[Model] = apps.get_model(data["model"])
        except Exception as e:
            self.stderr.write(self.style.ERROR(
                f"An error occurred while trying to find the model "
                f"{ data['model'] }: " + str(e)
            ))
            return

        # Get the field data from the JSON data
        fields: Dict[str, str] = data["fields"]

        # Insert the record into the database table
        try:
            model.objects.create(**fields)
        except IntegrityError:
            self.stdout.write(f"Data already exists!")
            return
        except Exception as e:
            self.stderr.write(self.style.ERROR(
                "An error occurred while trying to insert data into table: "
                + str(e)
            ))
            return

        self.stdout.write(
            self.style.SUCCESS(f"Loaded { json_file } into { str(model) }.")
        )
