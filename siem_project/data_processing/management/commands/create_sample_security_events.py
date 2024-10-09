from django.core.management.base import BaseCommand
from data_processing.models import SecurityEvent
from django.utils import timezone
import random

class Command(BaseCommand):
    help = 'Creates sample security events'

    def handle(self, *args, **options):
        event_types = ['LOGIN', 'FIREWALL', 'IDS', 'MALWARE']
        severities = [1, 2, 3, 4]  # Corresponding to Low, Medium, High, Critical

        for _ in range(20):  # Create 20 sample events
            SecurityEvent.objects.create(
                event_id=f"SAMPLE-{random.randint(1000, 9999)}",
                event_type=random.choice(event_types),
                source_ip=f"192.168.1.{random.randint(1, 255)}",
                destination_ip=f"10.0.0.{random.randint(1, 255)}",
                timestamp=timezone.now(),
                severity=random.choice(severities),
                description=f"Sample security event of type {random.choice(event_types)}",
                raw_data={"sample": "data"}
            )

        self.stdout.write(self.style.SUCCESS('Successfully created sample security events'))