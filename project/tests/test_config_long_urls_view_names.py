from django.urls import reverse
from django.test import TestCase
from mock import Mock
from silk.model_factory import RequestModelFactory


class TestLongRequestUrl(TestCase):

    def test_no_long_url(self):
        url = '1234567890' * 19  # 190-character URL
        mock_request = Mock()
        mock_request.META = {'CONTENT_TYPE': 'text/plain'}
        mock_request.GET = {}
        mock_request.path = url
        mock_request.method = 'get'
        request_model = RequestModelFactory(mock_request).construct_request_model()
        self.assertEqual(request_model.path, url)

    def test_long_url(self):
        url = '1234567890' * 200  # 2000-character URL
        mock_request = Mock()
        mock_request.META = {'CONTENT_TYPE': 'text/plain'}
        mock_request.GET = {}
        mock_request.method = 'get'
        mock_request.path = url
        request_model = RequestModelFactory(mock_request).construct_request_model()
        self.assertEqual(request_model.path, '%s...%s' % (url[:94], url[1907:]))


class TestLongRequestViewName(TestCase):

    def test_no_long_view_name(self):
        view_name = '1234567890' * 19  # 190-character view_name
        mock_request = Mock()
        mock_request.META = {'CONTENT_TYPE': 'text/plain'}
        mock_request.GET = {}
        mock_request.path = reverse('silk:requests')
        mock_request.method = 'get'
        request_model = RequestModelFactory(mock_request).construct_request_model()
        # We have to artifically assign view_name and save, as construct_request_model() will leave it empty
        request_model.view_name.return_value = view_name
        request_model.save()
        self.assertEqual(request_model.view_name, view_name)

    def test_long_view_name(self):
        view_name = '1234567890' * 200  # 2000-character view_name
        mock_request = Mock()
        mock_request.META = {'CONTENT_TYPE': 'text/plain'}
        mock_request.GET = {}
        mock_request.path = reverse('silk:requests')
        mock_request.method = 'get'
        request_model = RequestModelFactory(mock_request).construct_request_model()
        # We have to artifically assign view_name and save, as construct_request_model() will leave it empty
        request_model.view_name.return_value = view_name
        request_model.save()
        self.assertEqual(request_model.view_name, '%s...%s' % (view_name[:94], view_name[1907:]))
