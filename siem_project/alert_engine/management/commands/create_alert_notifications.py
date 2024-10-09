from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from alert_engine.models import AlertNotification

User = get_user_model()

class Command(BaseCommand):
    help = 'Creates AlertNotification objects for all existing users'

    def handle(self, *args, **options):
        users = User.objects.all()
        created_count = 0
        for user in users:
            _, created = AlertNotification.objects.get_or_create(
                user=user,
                defaults={
                    'severity_level': 2,
                    'email_notification': True
                }
            )
            if created:
                created_count += 1
        
        self.stdout.write(self.style.SUCCESS(f'Successfully created {created_count} AlertNotification objects'))