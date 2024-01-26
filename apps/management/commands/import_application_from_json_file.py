import io
import json
from json import decoder
from typing import Any

from django.core.management import BaseCommand, CommandParser
from rest_framework.exceptions import ValidationError

from apps.models import Application
from apps.serializers import ApplicationSerializer


class Command(BaseCommand):
    help = 'Import application from a JSON file.'

    def add_arguments(self, parser: CommandParser) -> None:
        """Add arguments to the parser.

        args:
            parser: CommandParser
        """
        parser.add_argument('file_path', type=str)
        parser.add_argument('--rewrite', action='store_true', default=False)

    def handle(self, *args: Any, **options: Any) -> None:
        """Import an Application from the file."""
        file_path = options.get('file_path')
        rewrite_app = options.get('rewrite')

        with io.open(file_path) as file_object:
            file_data = file_object.read()
            try:
                jsonyfied_file_data = json.loads(file_data)
            except decoder.JSONDecodeError:
                self.stdout.write(
                    self.style.ERROR('Incompatible file type. JSON file is expected.')
                )
                return
            try:
                if rewrite_app:
                    old_application = Application.objects.filter(slug=jsonyfied_file_data.get('slug'))
                    if not old_application:
                        self.stdout.write(
                            self.style.ERROR('Application with the given slug was not found. If you want to create a'
                                             'new application please remove the rewrite flag.')
                        )
                    serialized_application = ApplicationSerializer(old_application, data=jsonyfied_file_data)
                else:
                    serialized_application = ApplicationSerializer(data=jsonyfied_file_data)
                serialized_application.is_valid(raise_exception=True)
                application = serialized_application.save()
            except ValidationError as error:
                self.stdout.write(
                    self.style.ERROR(f"Validation Errors: [{error}]")
                )
                return

        self.stdout.write(
            self.style.SUCCESS(f"Successfully imported Application. id - {application.id}")
        )
