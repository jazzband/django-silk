from django.apps import apps as proj_apps
from django.test import TestCase

from silk.apps import SilkAppConfig


class TestAppConfig(TestCase):
    """
    Test if correct AppConfig class is loaded by Django.
    """

    def test_app_config_loaded(self):
        silk_app_config = proj_apps.get_app_config("silk")
        self.assertIsInstance(silk_app_config, SilkAppConfig)
