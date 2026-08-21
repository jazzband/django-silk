from django.core.management.base import BaseCommand

from silk.utils.data_deletion import clear_silk_data


class Command(BaseCommand):
    help = "Clears silk's log of requests."

    def handle(self, *args, **options):
        # Preserve in-flight requests (no end_time yet) so response
        # finalization cannot hit IntegrityError on a deleted Request.
        clear_silk_data()
