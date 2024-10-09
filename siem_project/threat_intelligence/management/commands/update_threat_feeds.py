from django.core.management.base import BaseCommand
from threat_intelligence.services import update_threat_feeds
from django.utils import timezone
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Updates threat intelligence feeds'

    def add_arguments(self, parser):
        parser.add_argument('--otx-api-key', type=str, help='AlienVault OTX API Key')

    def handle(self, *args, **options):
        try:
            self.stdout.write(f"Starting threat feed update at {timezone.now()}")
            otx_api_key = options['otx_api_key'] or getattr(settings, 'ALIENVAULT_OTX_API_KEY', None)
            if not otx_api_key:
                self.stdout.write(self.style.WARNING("No AlienVault OTX API key provided. Skipping OTX feed update."))
            update_threat_feeds(otx_api_key)
            self.stdout.write(self.style.SUCCESS(f"Successfully updated threat feeds at {timezone.now()}"))
        except Exception as e:
            logger.error(f"Error updating threat feeds: {str(e)}")
            self.stdout.write(self.style.ERROR(f"Failed to update threat feeds: {str(e)}"))