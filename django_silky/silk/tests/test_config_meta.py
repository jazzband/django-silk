from django.core.urlresolvers import reverse
from django.test import TestCase
from silk.config import SilkyConfig
from silk.models import Request

__author__ = 'mtford'

class TestConfigMeta(TestCase):

    def _execute_request(self):
        Request.objects.all().delete()
        response = self.client.get(reverse('example_app:index'))
        self.assertTrue(response.status_code == 200)
        objs = Request.objects.all()
        self.assertEqual(objs.count(), 1)
        r = objs[0]
        return r

    def test_enabled(self):
        SilkyConfig().SILKY_META = True
        r = self._execute_request()
        self.assertTrue(r.meta_start_time and r.meta_end_time)

    def test_disabled(self):
        SilkyConfig().SILKY_META = False
        r = self._execute_request()
        self.assertFalse(r.meta_start_time or r.meta_end_time)