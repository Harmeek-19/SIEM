from django.core.management.base import BaseCommand
from threat_intelligence.models import IOC

class Command(BaseCommand):
    help = 'Clears all IOCs from the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force the deletion without confirmation',
        )

    def handle(self, *args, **options):
        if options['force']:
            self.clear_iocs()
        else:
            confirm = input("Are you sure you want to delete all IOCs? This action cannot be undone. (yes/no): ")
            if confirm.lower() == 'yes':
                self.clear_iocs()
            else:
                self.stdout.write(self.style.WARNING("Operation cancelled."))

    def clear_iocs(self):
        count = IOC.objects.count()
        IOC.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f"Successfully deleted {count} IOCs."))