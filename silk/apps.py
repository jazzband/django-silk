import django
from django.apps import AppConfig
from django.core.exceptions import ImproperlyConfigured


class SilkAppConfig(AppConfig):
    default_auto_field = "django.db.models.AutoField"
    name = "silk"

    def ready(self):
