import logging
from typing import Any

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone


class Command(BaseCommand):
    help = 'Delete outdated database records created by demo-user'

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger('django.management')

    def handle(self, *args: str, **options: str) -> None:
        """Get all database records created by the demo-user and delete every record
        that is older than DEMO_RECORDS_TTL seconds.

        Args:
            args: positional command arguments (not used, interface requirement).
            options: named command arguments (not used, interface requirement).

        Raises:
            CommandError if the application does not run in a DEMO mode.
        """
        if not settings.DEMO_MODE:
            raise CommandError('The application does not run in DEMO mode! Exiting...')

        user_model = get_user_model()
        demo_user = user_model.objects.get(username=settings.DEMO_USER_NAME)

        self.logger.info(f'Checking the outdated records created by the {demo_user.username} user...')
        time_threshold = timezone.now() - timezone.timedelta(seconds=settings.DEMO_RECORDS_TTL)
        demo_user.applications.filter(created_at__lt=time_threshold).delete()
        demo_user.resources.filter(created_at__lt=time_threshold).delete()
        demo_user.responses.filter(created_at__lt=time_threshold).delete()
        self.logger.info('Checking complete.')
