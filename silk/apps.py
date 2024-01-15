from django.apps import AppConfig
from django.db import connection

from silk.sql import SilkQueryWrapper


class SilkAppConfig(AppConfig):
    default_auto_field = "django.db.models.AutoField"
    name = "silk"

    def ready(self):
        # Add wrapper to db connection
        if not any(isinstance(wrapper, SilkQueryWrapper) for wrapper in connection.execute_wrappers):
            connection.execute_wrappers.append(SilkQueryWrapper())
