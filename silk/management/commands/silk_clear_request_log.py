from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import connection

from silk.utils.data_deletion import delete_model

import silk.models


class Command(BaseCommand):
    help = "Clears silk's log of requests."

    def handle(self, *args, **options):
        # Django takes a long time to traverse foreign key relations,
        # so delete in the order that makes it easy.
        delete_model(silk.models.Profile)
        delete_model(silk.models.SQLQuery)
        delete_model(silk.models.Response)
        delete_model(silk.models.Request)
