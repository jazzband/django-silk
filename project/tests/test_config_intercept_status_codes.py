from unittest.mock import NonCallableMock

from django.test import TestCase

from silk.collector import DataCollector
from silk.config import SilkyConfig
from silk.errors import SilkNotConfigured
from silk.middleware import SilkyMiddleware
from silk.models import Request

from .util import delete_all_models


def fake_get_response():
    def fake_response():
        return 'hello world'
    return fake_response


class TestConfigInterceptStatusCodes(TestCase):
    def tearDown(self):
        SilkyConfig().SILKY_INTERCEPT_STATUS_CODES = None

    def _mock_response(self, status_code):
        response = NonCallableMock()
        response.headers = {}
        response.status_code = status_code
        response.queries = []
        response.get = response.headers.get
        response.content = ''
        return response

    def _execute_request(self, status_code):
        delete_all_models(Request)
        DataCollector().configure(Request.objects.create())
        response = self._mock_response(status_code)
        SilkyMiddleware(fake_get_response)._process_response('', response)
        return Request.objects.count()

    def test_default_records_all_responses(self):
        SilkyConfig().SILKY_INTERCEPT_STATUS_CODES = None
        self.assertEqual(self._execute_request(200), 1)

    def test_records_matching_status_code(self):
        SilkyConfig().SILKY_INTERCEPT_STATUS_CODES = {500}
        self.assertEqual(self._execute_request(500), 1)

    def test_discards_non_matching_status_code(self):
        SilkyConfig().SILKY_INTERCEPT_STATUS_CODES = {500}
        self.assertEqual(self._execute_request(200), 0)

    def test_accepts_list_of_status_codes(self):
        SilkyConfig().SILKY_INTERCEPT_STATUS_CODES = [500, 501]
        self.assertEqual(self._execute_request(501), 1)

    def test_invalid_setting_raises(self):
        for invalid in ("500", 500, ["500"], [True]):
            SilkyConfig().SILKY_INTERCEPT_STATUS_CODES = invalid
            with self.assertRaises(SilkNotConfigured):
                SilkyMiddleware(fake_get_response)
