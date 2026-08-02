from django.http import HttpResponse
from django.test import TestCase


class TestResponseAssumptions(TestCase):

    def test_headers_present_in_http_response(self):
        """Verify that HttpResponse has a headers attribute, which ResponseModelFactory relies on."""
        django_response = HttpResponse()
        self.assertTrue(hasattr(django_response, 'headers'))
