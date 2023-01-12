from unittest.mock import Mock

from django.test import TestCase
from django.urls import reverse

from silk.model_factory import RequestModelFactory, multipart_form


class TestMultipartForms(TestCase):

    def test_no_max_request(self):
        mock_request = Mock()
        mock_request.headers = {'content-type': multipart_form}
        mock_request.GET = {}
        mock_request.path = reverse('silk:requests')
        mock_request.method = 'post'
        mock_request.body = Mock()
        request_model = RequestModelFactory(mock_request).construct_request_model()
        self.assertFalse(request_model.body)
        self.assertEqual(b"Raw body not available for multipart_form data, Silk is not showing file uploads.", request_model.raw_body)
        mock_request.body.assert_not_called()
