from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from threat_intelligence.models import IOC

User = get_user_model()

class Command(BaseCommand):
    help = 'Reassigns IOCs with non-existent user references to an existing user'

    def add_arguments(self, parser):
        parser.add_argument('user_id', type=int, help='ID of the user to reassign IOCs to')

    def handle(self, *args, **options):
        try:
            user = User.objects.get(id=options['user_id'])
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'User with ID {options["user_id"]} does not exist'))
            return

        affected_iocs = IOC.objects.filter(user__isnull=True)
        count = affected_iocs.update(user=user)

        self.stdout.write(self.style.SUCCESS(f'Successfully reassigned {count} IOCs to user {user.username}'))