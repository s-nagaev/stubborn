import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db.utils import IntegrityError


class Command(BaseCommand):
    help = ('Create a TECHNICAL Administrator account for testing and debugging purposes. '
            'The command is NOT intended to run in Production and will not work there.')

    def handle(self, *args: str, **options: str) -> None:
        """Command handler method. Creates a TECHNICAL superuser with login 'admin' and password 'admin'.

        Args:
            args: positional command arguments (not used, interface requirement).
            options: named command arguments (not used, interface requirement).

        Raises:
            CommandError if the command is run in a production environment.
        """
        if os.environ['DJANGO_SETTINGS_MODULE'] == 'stubborn.settings.production':
            raise CommandError('This command cannot be run in a production environment! '
                               'Use the "createsuperuser" command to create a superuser in a production environment.')
        username = 'admin'
        email = 'admin@example.com'
        password = 'admin'

        self.stdout.write(f'Add a technical superuser with name {username} and password {password}.')
        user = get_user_model()
        try:
            user.objects.create_superuser(username, email, password)
        except IntegrityError:
            self.stdout.write(f'A user named "{username}" already exists.')
