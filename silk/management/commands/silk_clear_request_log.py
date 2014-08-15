from django.core.management.base import BaseCommand, CommandError

import silk.models

class Command(BaseCommand):
	help = "Clears silk's log of requests."
	
	def handle(self, *args, **options):
		count = silk.models.Request.objects.count()
		print("deleting %s request objects" % count)
		silk.models.Request.objects.all().delete()
