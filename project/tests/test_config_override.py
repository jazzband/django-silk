from django.test import TestCase, override_settings

from silk.config import SilkyConfig


class TestOverrideSettings(TestCase):
    def test_respects_override_settings(self):
        with override_settings(SILKY_INTERCEPT_PERCENT=0):
            self.assertEqual(SilkyConfig().SILKY_INTERCEPT_PERCENT, 0)
