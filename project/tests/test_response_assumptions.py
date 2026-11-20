from django.http import HttpResponse
from django.test import TestCase

from silk.collector import DataCollector
from silk.model_factory import ResponseModelFactory
from silk.models import Request


class TestResponseAssumptions(TestCase):

    def test_headers_present_in_http_response(self):
        """Verify that HttpResponse has a headers attribute, which ResponseModelFactory relies on."""
        django_response = HttpResponse()
        self.assertTrue(hasattr(django_response, 'headers'))

    def test_two_character_header_values_are_recorded(self):
        DataCollector().request = Request.objects.create()
        django_response = HttpResponse()
        django_response['Content-Language'] = 'en'
        django_response['Content-Length'] = '42'
        response_model = ResponseModelFactory(django_response).construct_response_model()
        self.assertEqual(response_model.headers['content-language'], 'en')
        self.assertEqual(response_model.headers['content-length'], '42')
