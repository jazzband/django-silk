import json
from unittest.mock import Mock, PropertyMock

from django.core.exceptions import RequestDataTooBig
from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import QueryDict
from django.test import TestCase
from django.urls import reverse
from django.utils.datastructures import MultiValueDict

from silk.collector import DataCollector
from silk.config import SilkyConfig
from silk.model_factory import RequestModelFactory, ResponseModelFactory
from silk.models import Request


class TestMaxBodySizeRequest(TestCase):

    def test_no_max_request(self):
        SilkyConfig().SILKY_MAX_REQUEST_BODY_SIZE = -1
        mock_request = Mock()
        mock_request.headers = {'content-type': 'text/plain'}
        mock_request.GET = {}
        mock_request.path = reverse('silk:requests')
        mock_request.method = 'get'
        mock_request.body = b'a' * 1000  # 1000 bytes?
        request_model = RequestModelFactory(mock_request).construct_request_model()
        self.assertTrue(request_model.raw_body)

    def test_max_request(self):
        SilkyConfig().SILKY_MAX_REQUEST_BODY_SIZE = 10  # 10kb
        mock_request = Mock()
        mock_request.headers = {'content-type': 'text/plain'}
        mock_request.GET = {}
        mock_request.method = 'get'
        mock_request.body = b'a' * 1024 * 100  # 100kb
        mock_request.path = reverse('silk:requests')
        request_model = RequestModelFactory(mock_request).construct_request_model()
        self.assertFalse(request_model.raw_body)

    def test_request_data_too_big(self):
        """
        When Django refuses to read the body (DATA_UPLOAD_MAX_MEMORY_SIZE), the
        parsed form data is stored as JSON, with uploads reduced to their file
        names and sensitive values masked.
        """
        SilkyConfig().SILKY_MAX_REQUEST_BODY_SIZE = -1
        mock_request = Mock()
        mock_request.headers = {'content-type': 'application/x-www-form-urlencoded'}
        mock_request.GET = {}
        mock_request.path = reverse('silk:requests')
        mock_request.method = 'post'
        type(mock_request).body = PropertyMock(side_effect=RequestDataTooBig())
        mock_request.POST = QueryDict('username=bob&password=hunter2&note=hello')
        mock_request.FILES = MultiValueDict({
            'upload': [SimpleUploadedFile('report.pdf', b'x' * 10)],
        })

        request_model = RequestModelFactory(mock_request).construct_request_model()

        self.assertEqual(
            b"Raw body exceeds DATA_UPLOAD_MAX_MEMORY_SIZE, Silk is not showing file uploads.",
            request_model.raw_body,
        )
        self.assertNotIn('hunter2', request_model.body)
        self.assertEqual(
            json.loads(request_model.body),
            {
                'note': ['hello'],
                'password': RequestModelFactory.CLEANSED_SUBSTITUTE,
                'upload': ['report.pdf'],
                'username': RequestModelFactory.CLEANSED_SUBSTITUTE,
            },
        )


class TestMaxBodySizeResponse(TestCase):

    def setUp(self):
        DataCollector().request = Request.objects.create()

    def test_no_max_response(self):
        SilkyConfig().SILKY_MAX_RESPONSE_BODY_SIZE = -1
        mock_response = Mock()
        mock_response.headers = {'content-type': 'text/plain'}
        mock_response.content = b'a' * 1000  # 1000 bytes?
        mock_response.status_code = 200
        mock_response.get = mock_response.headers.get
        response_model = ResponseModelFactory(mock_response).construct_response_model()
        self.assertTrue(response_model.raw_body)

    def test_max_response(self):
        SilkyConfig().SILKY_MAX_RESPONSE_BODY_SIZE = 10  # 10kb
        mock_response = Mock()
        mock_response.headers = {'content-type': 'text/plain'}
        mock_response.content = b'a' * 1024 * 100  # 100kb
        mock_response.status_code = 200
        mock_response.get = mock_response.headers.get
        response_model = ResponseModelFactory(mock_response).construct_response_model()
        self.assertFalse(response_model.raw_body)
