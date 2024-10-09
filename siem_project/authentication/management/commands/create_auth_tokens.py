from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token

User = get_user_model()

class Command(BaseCommand):
    help = 'Creates auth tokens for existing users'

    def handle(self, *args, **options):
        users = User.objects.all()
        for user in users:
            Token.objects.get_or_create(user=user)
        self.stdout.write(self.style.SUCCESS('Successfully created tokens for all users'))