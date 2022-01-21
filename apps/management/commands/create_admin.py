import logging
import os
from argparse import RawTextHelpFormatter
from typing import Any

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandParser

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = (
        """Create a superuser with login, email and password according to environment variables:
        - ADMIN_USERNAME
        - ADMIN_EMAIL
        - ADMIN_PASSWORD"""
    )

    def create_parser(self, prog_name: str, subcommand: str, **kwargs: Any) -> CommandParser:
        parser = super().create_parser(prog_name, subcommand, **kwargs)
        parser.formatter_class = RawTextHelpFormatter
        return parser

    def handle(self, *args: str, **options: str) -> None:
        """Create a regular superuser account.

        Args:
            args: positional command arguments (not used, interface requirement).
            options: named command arguments (not used, interface requirement).

        Raises:
            CommandError if the command is run in a production environment.
        """
        username = os.environ.get('ADMIN_USERNAME')
        password = os.environ.get('ADMIN_PASSWORD')
        email = os.environ.get('ADMIN_EMAIL')

        if not username or not password or not email:
            logger.info('No environment variables for the superuser account creation provided.')
            return

        user = get_user_model()

        if user.objects.filter(username=username).exists():
            logger.info('A superuser with the username "%s" is already exists.', username)
            return

        user.objects.create_superuser(username, email, password)
        logger.info('A superuser account with the username "%s" was created successfully', username)
