from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Setup threat intelligence: run migrations, create initial data, and update threat feeds'

    def add_arguments(self, parser):
        parser.add_argument('--otx-api-key', type=str, help='AlienVault OTX API Key')

    def handle(self, *args, **options):
        try:
            self.stdout.write("Running migrations...")
            call_command('migrate')

            self.stdout.write("Creating initial data...")
            # The signal handler will create initial data after migrations

            self.stdout.write("Updating threat feeds...")
            otx_api_key = options['otx_api_key'] or getattr(settings, 'ALIENVAULT_OTX_API_KEY', None)
            if not otx_api_key:
                self.stdout.write(self.style.WARNING("No AlienVault OTX API key provided. Skipping OTX feed update."))
            call_command('update_threat_feeds', otx_api_key=otx_api_key)

            self.stdout.write(self.style.SUCCESS("Threat intelligence setup completed successfully"))
        except Exception as e:
            logger.error(f"Error during threat intelligence setup: {str(e)}")
            self.stdout.write(self.style.ERROR(f"Failed to setup threat intelligence: {str(e)}"))