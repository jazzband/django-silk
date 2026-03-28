import datetime

from django.core.management.base import BaseCommand
from django.utils import timezone

from silk.models import Request


class Command(BaseCommand):
    help = 'Clears profiling data (requests, SQL queries, profiles, etc.) older than a specified number of days.'

    def add_arguments(self, parser):
        parser.add_argument(
            'days',
            type=int,
            help='Number of days to keep. Data older than this will be deleted.'
        )

    def handle(self, *args, **options):
        days = options['days']

        if days < 0:
            self.stderr.write(self.style.ERROR('Days must be a non-negative integer.'))
            return

        cutoff_date = timezone.now() - datetime.timedelta(days=days)

        self.stdout.write(self.style.NOTICE(f'Deleting profiling data older than {cutoff_date.isoformat()}...'))

        deleted_count, _ = Request.objects.filter(start_time__lt=cutoff_date).delete()

        self.stdout.write(self.style.SUCCESS(f'Successfully deleted {deleted_count} profiling requests.'))
