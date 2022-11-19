from django.core.management.base import BaseCommand

import silk.models
from silk.config import SilkyConfig


class Command(BaseCommand):
    help = "Triggers silk's request garbage collect."

    def add_arguments(self, parser):
        parser.add_argument(
            "-m",
            "--max-requests",
            default=SilkyConfig().SILKY_MAX_RECORDED_REQUESTS,
            type=int,
            help="Maximum number of requests to keep after garbage collection.",
        )

    def handle(self, *args, **options):
        if "max_requests" in options:
            max_requests = options["max_requests"]
            SilkyConfig().SILKY_MAX_RECORDED_REQUESTS = max_requests
        if options["verbosity"] >= 2:
            max_requests = SilkyConfig().SILKY_MAX_RECORDED_REQUESTS
            request_count = silk.models.Request.objects.count()
            self.stdout.write(
                f"Keeping up to {max_requests} of {request_count} requests."
            )
        silk.models.Request.garbage_collect(force=True)
