import json
from unittest.mock import Mock, patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import RequestFactory, TestCase
from django.urls import reverse

from silk.config import SilkyConfig
from silk.model_factory import RequestModelFactory, multipart_form
from silk.models import Request


class TestMultipartForms(TestCase):

    def setUp(self):
        self.factory = RequestFactory()

    def test_body_does_not_read_request(self):
        mock_request = Mock()
        mock_request.headers = {'content-type': multipart_form}
        mock_request.GET = {}
        mock_request.path = reverse('silk:requests')
        mock_request.method = 'post'
        request_model = RequestModelFactory(mock_request).construct_request_model()
        self.assertFalse(request_model.body)
        self.assertEqual(request_model.raw_body, '')
        # Neither the raw body nor the parsed form data may be touched before the view runs
        self.assertEqual(
            [c for c in mock_request.mock_calls if c[0].split('.')[0] in ('body', 'POST', 'FILES', 'read')],
            [],
        )

    def test_multipart_with_form_fields(self):
        request = self.factory.post('/', {'username': 'testuser', 'email': 'test@example.com'})
        body = json.loads(RequestModelFactory(request).multipart_body())
        self.assertEqual(body['email'], 'test@example.com')
        # username is a sensitive key and should be masked
        self.assertNotEqual(body.get('username'), 'testuser')

    def test_multipart_with_repeated_field(self):
        request = self.factory.post('/', {'tag': ['a', 'b']})
        body = json.loads(RequestModelFactory(request).multipart_body())
        self.assertEqual(body['tag'], ['a', 'b'])

    def test_multipart_with_files(self):
        upload = SimpleUploadedFile('document.pdf', b'x' * 123, content_type='application/pdf')
        request = self.factory.post('/', {'attachment': upload})
        body = json.loads(RequestModelFactory(request).multipart_body())
        self.assertEqual(body['_files']['attachment'], {
            'name': 'document.pdf',
            'size': 123,
            'content_type': 'application/pdf',
        })

    def test_multipart_with_form_fields_and_files(self):
        upload = SimpleUploadedFile('photo.jpg', b'jpeg', content_type='image/jpeg')
        request = self.factory.post('/', {'title': 'My Document', 'image': upload})
        body = json.loads(RequestModelFactory(request).multipart_body())
        self.assertEqual(body['title'], 'My Document')
        self.assertEqual(body['_files']['image']['name'], 'photo.jpg')

    def test_multipart_empty_form(self):
        request = self.factory.post('/', {})
        self.assertEqual(RequestModelFactory(request).multipart_body(), '')

    def test_multipart_after_view_read_body(self):
        request = self.factory.post('/', {'title': 'x'})
        request.body  # the view read the raw body
        body = json.loads(RequestModelFactory(request).multipart_body())
        self.assertEqual(body['title'], 'x')

    def test_multipart_after_view_read_stream(self):
        request = self.factory.post('/', {'title': 'x'})
        request.read()  # the view consumed the stream directly; the data is gone
        self.assertEqual(RequestModelFactory(request).multipart_body(), '')

    def test_multipart_put_is_not_parsed(self):
        request = self.factory.put('/', {'title': 'x'}, content_type=multipart_form)
        self.assertEqual(RequestModelFactory(request).multipart_body(), '')

    def test_not_multipart(self):
        request = self.factory.post('/', {'title': 'x'}, content_type='application/json')
        self.assertEqual(RequestModelFactory(request).multipart_body(), '')

    def test_multipart_parse_error_is_ignored(self):
        request = self.factory.post(
            '/', b'not multipart', content_type='multipart/form-data; boundary=BoUnDaRy'
        )
        with patch.object(RequestModelFactory, '_parse_multipart_body', side_effect=ValueError('bad')):
            self.assertEqual(RequestModelFactory(request).multipart_body(), '')


class TestMultipartMiddleware(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        SilkyConfig().SILKY_META = False

    def test_form_data_recorded_after_view(self):
        upload = SimpleUploadedFile('photo.jpg', b'jpeg', content_type='image/jpeg')
        response = self.client.post(
            reverse('example_app:upload_test'), {'title': 'My Document', 'image': upload}
        )
        self.assertEqual(response.json(), {'fields': {'title': 'My Document'}, 'files': {'image': 'photo.jpg'}})
        silk_request = Request.objects.get(path=reverse('example_app:upload_test'))
        body = json.loads(silk_request.body)
        self.assertEqual(body['title'], 'My Document')
        self.assertEqual(body['_files']['image']['name'], 'photo.jpg')
        self.assertEqual(silk_request.raw_body, '')

    def test_view_can_read_raw_body(self):
        """Silk must not consume the stream before the view reads request.body."""
        response = self.client.post(reverse('example_app:upload_raw_body_test'), {'title': 'x'})
        self.assertEqual(response.status_code, 200)
        self.assertGreater(response.json()['length'], 0)
        silk_request = Request.objects.get(path=reverse('example_app:upload_raw_body_test'))
        self.assertEqual(json.loads(silk_request.body)['title'], 'x')
