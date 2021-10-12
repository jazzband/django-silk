from django.test import TestCase
from unittest.mock import Mock
from silk.model_factory import RequestModelFactory


class TestLongRequestUrl(TestCase):
    def test_no_long_url(self):
        url = "1234567890" * 19  # 190-character URL
        mock_request = Mock()
        mock_request.META = {"CONTENT_TYPE": "text/plain"}
        mock_request.GET = {}
        mock_request.path = url
        mock_request.method = "get"
        request_model = RequestModelFactory(mock_request).construct_request_model()
        self.assertEqual(request_model.path, url)

    def test_long_url(self):
        url = "1234567890" * 200  # 2000-character URL
        mock_request = Mock()
        mock_request.META = {"CONTENT_TYPE": "text/plain"}
        mock_request.GET = {}
        mock_request.method = "get"
        mock_request.path = url
        request_model = RequestModelFactory(mock_request).construct_request_model()
        self.assertEqual(request_model.path, "%s...%s" % (url[:94], url[1907:]))
        self.assertEqual(len(request_model.path), 190)
