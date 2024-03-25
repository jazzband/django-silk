from unittest.mock import Mock

from django.test import TestCase
from django.urls import reverse

from silk.model_factory import RequestModelFactory, multipart_form


class TestMultipartForms(TestCase):

    def setUp(self):
        self.mock_request = Mock()
        self.mock_request.method = "POST"
        self.mock_request.GET = {}
        self.mock_request.path = reverse("silk:requests")
        self.mock_request.headers = {"content-type": multipart_form}
        self.mock_request.FILES = {"file": "file.txt", "file2": "file2.pdf", "file3": "file3.jpg"}

    def test_no_max_request(self):
        mock_request = Mock()
        mock_request.headers = {"content-type": multipart_form}
        mock_request.GET = {}
        mock_request.path = reverse("silk:requests")
        mock_request.method = "post"
        mock_request.body = Mock()
        request_model = RequestModelFactory(mock_request).construct_request_model()
        self.assertFalse(request_model.body)
        self.assertEqual(
            b"Raw body not available for multipart_form data, Silk is not showing file uploads.",
            request_model.raw_body,
        )
        mock_request.body.assert_not_called()

    def test_multipart_form_request_creation_raises_no_exception(self):
        """ 
        Test that a request with multipart form data is created correctly without raising excetions
        """
        request_model = RequestModelFactory(self.mock_request).construct_request_model()
        self.assertTrue(request_model.body)
        self.assertEqual(
            {
                'form_data': {},
                'files': {
                    'file': 'file.txt',
                    'file2': 'file2.pdf',
                    'file3': 'file3.jpg'
                }
            },
            request_model.body
        )
        self.assertIsNone(request_model.raw_body)
