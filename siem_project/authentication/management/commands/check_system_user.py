from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token

class Command(BaseCommand):
    help = 'Check if system user exists and has a valid token'

    def handle(self, *args, **options):
        User = get_user_model()
        try:
            system_user = User.objects.get(username='system_user')
            token, created = Token.objects.get_or_create(user=system_user)
            self.stdout.write(self.style.SUCCESS(f'System user exists. Token: {token.key}'))
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR('System user does not exist'))