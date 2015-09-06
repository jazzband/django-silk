from django.core.management.base import BaseCommand, CommandError

import silk.models


class Command(BaseCommand):
    help = "Clears silk's log of requests."

    @staticmethod
    def delete_model(model):
        count = model.objects.count()
        print("deleting %s %s objects" % (model.__name__, count))
        model.objects.all().delete()

    def handle(self, *args, **options):
        # Django takes a long time to traverse foreign key relations,
        # so delete in the order that makes it easy.
        Command.delete_model(silk.models.Profile)
        Command.delete_model(silk.models.SQLQuery)
        Command.delete_model(silk.models.Response)
        Command.delete_model(silk.models.Request)
