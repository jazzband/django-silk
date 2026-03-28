from django.apps import AppConfig
import django
from django.core.exceptions import ImproperlyConfigured


class SilkAppConfig(AppConfig):
    default_auto_field = "django.db.models.AutoField"
    name = "silk"

    def ready(self):
        if django.VERSION < (4, 2):
            raise ImproperlyConfigured(
                'Django Silk requires Django 4.2 or later. '
                'Please upgrade your Django version.'
            )
