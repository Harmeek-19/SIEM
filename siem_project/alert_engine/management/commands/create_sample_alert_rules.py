from django.core.management.base import BaseCommand
from alert_engine.models import AlertRule

class Command(BaseCommand):
    help = 'Creates sample alert rules'

    def handle(self, *args, **options):
        rules = [
            {
                "name": "High Severity Event",
                "description": "Alert on any high severity event",
                "condition": "severity>=3",
                "severity": 3,
            },
            {
                "name": "Frequent Login Attempts",
                "description": "Alert on frequent login attempts",
                "condition": "event_type='LOGIN' AND count > 10",
                "severity": 2,
            },
            {
                "name": "Suspicious IP Access",
                "description": "Alert on access from suspicious IP",
                "condition": "source_ip IN ('10.0.0.1', '192.168.1.1')",
                "severity": 3,
            },
            {
                "name": "Off-hours Activity",
                "description": "Alert on activity outside business hours",
                "condition": "hour(timestamp) NOT BETWEEN 9 AND 17",
                "severity": 2,
            },
            {
                "name": "Critical System Access",
                "description": "Alert on access to critical systems",
                "condition": "event_type='SYSTEM' AND description LIKE '%critical%'",
                "severity": 4,
            },
            {
                "name": "Malware Detection",
                "description": "Alert on potential malware activity",
                "condition": "event_type='MALWARE'",
                "severity": 4,
            },
        ]

        for rule in rules:
            AlertRule.objects.create(
                name=rule["name"],
                description=rule["description"],
                condition=rule["condition"],
                severity=rule["severity"],
                enabled=True
            )

        self.stdout.write(self.style.SUCCESS(f'Successfully created {len(rules)} sample alert rules'))