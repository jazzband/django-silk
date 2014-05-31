from django.conf import settings
from django.test import TestCase
from silk.config import SilkyConfig


class TestSilkyConfig(TestCase):

    def test_silk_defaults(self):
        settings.SILKY_DYNAMIC_PROFILING = ['something']
        config = SilkyConfig()
        self.assertFalse(config.SILKY_DEBUG)
        self.assertListEqual(config.SILKY_DYNAMIC_PROFILING, ['something'])