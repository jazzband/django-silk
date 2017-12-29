try:
    # Django >= 1.10
    from django.urls import reverse
except ImportError:
    # Django < 2.0
    from django.core.urlresolvers import reverse
from django.test import TestCase
from mock import Mock
from silk.model_factory import RequestModelFactory, ResponseModelFactory
from silk.models import Request
from silk.collector import DataCollector
from silk.config import SilkyConfig


class TestMaxBodySizeRequest(TestCase):

    def test_no_max_request(self):
        SilkyConfig().SILKY_MAX_REQUEST_BODY_SIZE = -1
        mock_request = Mock()
        mock_request.META = {'CONTENT_TYPE': 'text/plain'}
        mock_request.GET = {}
        mock_request.path = reverse('silk:requests')
        mock_request.method = 'get'
        mock_request.body = 'a'.encode('ascii') * 1000  # 1000 bytes?
        request_model = RequestModelFactory(mock_request).construct_request_model()
        self.assertTrue(request_model.raw_body)

    def test_max_request(self):
        SilkyConfig().SILKY_MAX_REQUEST_BODY_SIZE = 10  # 10kb
        mock_request = Mock()
        mock_request.META = {'CONTENT_TYPE': 'text/plain'}
        mock_request.GET = {}
        mock_request.method = 'get'
        mock_request.body = 'a'.encode('ascii') * 1024 * 100  # 100kb
        mock_request.path = reverse('silk:requests')
        request_model = RequestModelFactory(mock_request).construct_request_model()
        self.assertFalse(request_model.raw_body)

class TestMaxBodySizeResponse(TestCase):

    def setUp(self):
        DataCollector().request = Request.objects.create()

    def test_no_max_response(self):
        SilkyConfig().SILKY_MAX_RESPONSE_BODY_SIZE = -1
        mock_response = Mock()
        headers = {'CONTENT_TYPE': 'text/plain'}
        mock_response.get = headers.get
        mock_response._headers = headers
        mock_response.content = 'a'.encode('ascii') * 1000  # 1000 bytes?
        mock_response.status_code = 200
        response_model = ResponseModelFactory(mock_response).construct_response_model()
        self.assertTrue(response_model.raw_body)

    def test_max_response(self):
        SilkyConfig().SILKY_MAX_RESPONSE_BODY_SIZE = 10  # 10kb
        mock_response = Mock()
        headers = {'CONTENT_TYPE': 'text/plain'}
        mock_response.get = headers.get
        mock_response._headers = headers
        mock_response.content = 'a'.encode('ascii') * 1024 * 100  # 100kb
        mock_response.status_code = 200
        response_model = ResponseModelFactory(mock_response).construct_response_model()
        self.assertFalse(response_model.raw_body)
