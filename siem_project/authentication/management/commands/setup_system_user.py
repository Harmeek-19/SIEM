# File: authentication/management/commands/setup_system_user.py

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
import secrets
import string

User = get_user_model()

class Command(BaseCommand):
    help = 'Sets up the system user for SIEM operations'

    def handle(self, *args, **options):
        username = 'system_user'
        email = 'system@example.com'
        password = ''.join(secrets.choice(string.ascii_letters + string.digits) for i in range(20))

        try:
            system_user = User.objects.get(username=username)
            self.stdout.write(self.style.SUCCESS(f'System user already exists: {username}'))
        except User.DoesNotExist:
            system_user = User.objects.create_user(username=username, email=email, password=password)
            system_user.is_staff = True
            system_user.is_superuser = True
            system_user.save()
            self.stdout.write(self.style.SUCCESS(f'Successfully created system user: {username}'))
            self.stdout.write(self.style.WARNING(f'Generated password: {password}'))

        token, created = Token.objects.get_or_create(user=system_user)
        self.stdout.write(self.style.SUCCESS(f'System user token: {token.key}'))

        self.stdout.write(self.style.WARNING('Please store the token and password securely and update your configuration if necessary.'))