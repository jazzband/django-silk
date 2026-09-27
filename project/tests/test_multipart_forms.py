import json
from unittest.mock import Mock, PropertyMock

from django.http import QueryDict
from django.http.multipartparser import MultiPartParserError
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
        mock_request.POST = QueryDict()
        mock_request.FILES = {}
        request_model = RequestModelFactory(mock_request).construct_request_model()
        self.assertFalse(request_model.body)
        self.assertEqual(request_model.raw_body, '')
        mock_request.body.assert_not_called()

    def test_multipart_with_form_fields(self):
        mock_request = Mock()
        mock_request.headers = {'content-type': multipart_form}
        mock_request.GET = {}
        mock_request.path = reverse('silk:requests')
        mock_request.method = 'post'
        mock_request.body = Mock()
        post_data = QueryDict(mutable=True)
        post_data['username'] = 'testuser'
        post_data['email'] = 'test@example.com'
        mock_request.POST = post_data
        mock_request.FILES = {}
        request_model = RequestModelFactory(mock_request).construct_request_model()
        body = json.loads(request_model.body)
        self.assertEqual(body['email'], 'test@example.com')
        # username is a sensitive key and should be masked
        self.assertNotEqual(body.get('username'), 'testuser')
        mock_request.body.assert_not_called()

    def test_multipart_with_files(self):
        mock_request = Mock()
        mock_request.headers = {'content-type': multipart_form}
        mock_request.GET = {}
        mock_request.path = reverse('silk:requests')
        mock_request.method = 'post'
        mock_request.body = Mock()
        mock_request.POST = QueryDict()
        mock_file = Mock()
        mock_file.name = 'document.pdf'
        mock_file.size = 12345
        mock_file.content_type = 'application/pdf'
        mock_request.FILES = {'attachment': mock_file}
        request_model = RequestModelFactory(mock_request).construct_request_model()
        body = json.loads(request_model.body)
        self.assertIn('_files', body)
        self.assertEqual(body['_files']['attachment']['name'], 'document.pdf')
        self.assertEqual(body['_files']['attachment']['size'], 12345)
        self.assertEqual(body['_files']['attachment']['content_type'], 'application/pdf')
        mock_request.body.assert_not_called()

    def test_multipart_with_form_fields_and_files(self):
        mock_request = Mock()
        mock_request.headers = {'content-type': multipart_form}
        mock_request.GET = {}
        mock_request.path = reverse('silk:requests')
        mock_request.method = 'post'
        mock_request.body = Mock()
        post_data = QueryDict(mutable=True)
        post_data['title'] = 'My Document'
        mock_request.POST = post_data
        mock_file = Mock()
        mock_file.name = 'photo.jpg'
        mock_file.size = 54321
        mock_file.content_type = 'image/jpeg'
        mock_request.FILES = {'image': mock_file}
        request_model = RequestModelFactory(mock_request).construct_request_model()
        body = json.loads(request_model.body)
        self.assertEqual(body['title'], 'My Document')
        self.assertIn('_files', body)
        self.assertEqual(body['_files']['image']['name'], 'photo.jpg')
        mock_request.body.assert_not_called()

    def test_multipart_parse_error_is_ignored(self):
        mock_request = Mock()
        mock_request.headers = {'content-type': multipart_form}
        mock_request.GET = {}
        mock_request.path = reverse('silk:requests')
        mock_request.method = 'post'
        mock_request.body = Mock()
        type(mock_request).POST = PropertyMock(side_effect=MultiPartParserError('bad'))
        type(mock_request).FILES = PropertyMock(side_effect=MultiPartParserError('bad'))
        request_model = RequestModelFactory(mock_request).construct_request_model()
        self.assertFalse(request_model.body)
        self.assertEqual(request_model.raw_body, '')
        mock_request.body.assert_not_called()
