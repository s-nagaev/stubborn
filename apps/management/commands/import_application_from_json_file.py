import io
import json
from typing import Any

from django.core.management import BaseCommand
from django.core.management.base import CommandParser
from rest_framework.exceptions import ValidationError

from apps.services import save_application_from_json_object


class Command(BaseCommand):
    help = 'Import application from a JSON file.'

    def add_arguments(self, parser: CommandParser) -> None:
        """Add arguments to the parser.

        args:
            parser: CommandParser
        """
        parser.add_argument('file_path', type=str)
        parser.add_argument('--update', action='store_true', default=False)

    def handle(self, *args: Any, **options: Any) -> None:
        """Import an Application from the file."""
        file_path = options.get('file_path', '')
        update = options.get('update')

        with io.open(file_path) as file_object:
            try:
                file_data = file_object.read()
                jsonyfied_file_data = json.loads(file_data)
                application = save_application_from_json_object(jsonyfied_file_data, update)
            except ValidationError as error:
                self.stdout.write(
                    self.style.ERROR(f"Validation Errors: [{error}]")
                )
                return

        self.stdout.write(
            self.style.SUCCESS(f"Successfully imported Application. id - {application.id}")
        )
