from django.core.management.base import BaseCommand
from django.utils import timezone


class Command(BaseCommand):
    help = 'Отображает текущее время'

    def handle(self, *args, **kwargs):
        time = timezone.now().strftime('%X')
        self.stdout.write(f"Текущее время: {time}")
