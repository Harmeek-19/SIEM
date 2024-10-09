import random
from django.core.management.base import BaseCommand
from django.utils import timezone
from data_processing.models import SecurityEvent

class Command(BaseCommand):
    help = 'Generates test security events'

    def handle(self, *args, **options):
        event_types = [choice[0] for choice in SecurityEvent.EVENT_TYPES]
        severity_levels = [choice[0] for choice in SecurityEvent.SEVERITY_LEVELS]
        
        for _ in range(100):  # Generate 100 random events
            event_type = random.choice(event_types)
            severity = random.choice(severity_levels)
            
            event = SecurityEvent.objects.create(
                event_id=f"TEST-{random.randint(1000, 9999)}",
                event_type=event_type,
                source_ip=f"192.168.{random.randint(1, 255)}.{random.randint(1, 255)}",
                destination_ip=f"10.0.{random.randint(1, 255)}.{random.randint(1, 255)}",
                timestamp=timezone.now() - timezone.timedelta(minutes=random.randint(0, 1440)),
                severity=severity,
                description=f"Test {event_type} event",
                raw_data={"test": "data"}
            )
            
            self.stdout.write(self.style.SUCCESS(f'Created event: {event}'))

        self.stdout.write(self.style.SUCCESS('Successfully generated test security events'))