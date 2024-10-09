from django.core.management.base import BaseCommand
from django.urls import get_resolver

class Command(BaseCommand):
    help = 'Prints all URL patterns'

    def handle(self, *args, **options):
        resolver = get_resolver()
        for url_pattern in resolver.url_patterns:
            self.stdout.write(self.style.SUCCESS(f'{url_pattern}'))