from django.core.management.base import BaseCommand
from django.utils import timezone
from threat_intelligence.models import IOC

class Command(BaseCommand):
    help = 'Clears IOCs older than a specified number of days'

    def add_arguments(self, parser):
        parser.add_argument('days', type=int, help='Number of days to keep')

    def handle(self, *args, **options):
        days = options['days']
        cutoff_date = timezone.now() - timezone.timedelta(days=days)
        old_iocs = IOC.objects.filter(last_seen__lt=cutoff_date)
        count = old_iocs.count()
        old_iocs.delete()
        self.stdout.write(self.style.SUCCESS(f'Successfully deleted {count} old IOCs'))