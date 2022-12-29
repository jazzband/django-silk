from django.test import Client, TestCase
from silk.models import Request
from django.urls import reverse
from http import HTTPStatus

class TestDeleteRequest(TestCase):
    def setUp(self):
        self.client = Client()
        self.request = Request()
        self.request.path = reverse('silk:requests')
        self.request.method = 'get'
        self.request.body = b'a' * 1000
        self.request.save()
    
    def test_delete(self):
        response = self.client.post(reverse('silk:request_detail', kwargs={'request_id':str(self.request.id)}))
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
