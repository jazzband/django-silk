from django.test import TestCase
from mock import NonCallableMock

from silk.collector import DataCollector
from silk.middleware import SilkyMiddleware

from silk.tests.util import delete_all_models
from silk.config import SilkyConfig
from silk.models import Request


class TestConfigMeta(TestCase):
    def _mock_response(self):
        response = NonCallableMock()
        response._headers = {}
        response.status_code = 200
        response.queries = []
        response.get = response._headers.get
        response.content = ''
        return response

    def _execute_request(self):
        delete_all_models(Request)
        DataCollector().configure(Request.objects.create())
        response = self._mock_response()
        SilkyMiddleware()._process_response(response)
        self.assertTrue(response.status_code == 200)
        objs = Request.objects.all()
        self.assertEqual(objs.count(), 1)
        r = objs[0]
        return r

    def test_enabled(self):
        SilkyConfig().SILKY_META = True
        r = self._execute_request()
        self.assertTrue(r.meta_time)

    def test_disabled(self):
        SilkyConfig().SILKY_META = False
        r = self._execute_request()
        self.assertFalse(r.meta_time)