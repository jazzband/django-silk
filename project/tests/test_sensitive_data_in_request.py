# coding=utf-8

import json

from django.test import TestCase
from mock import Mock

from silk.model_factory import RequestModelFactory, ResponseModelFactory

DJANGO_META_CONTENT_TYPE = 'CONTENT_TYPE'
HTTP_CONTENT_TYPE = 'Content-Type'


class TestEncodingForRequests(TestCase):
    """
    Check that the RequestModelFactory masks sensitive data
    """

    def test_password_in_body(self):
        mock_request = Mock()
        mock_request.META = {DJANGO_META_CONTENT_TYPE: 'text/plain'}
        mock_request.body = 'username=test_username&unmasked=testunmasked&password=testpassword'
        mock_request.get = mock_request.META.get
        factory = RequestModelFactory(mock_request)
        body, raw_body = factory.body()

        self.assertIn('testunmasked', raw_body)
        self.assertNotIn('test_username', raw_body)
        self.assertNotIn('testpassword', raw_body)
        self.assertNotIn('test_username', body)
        self.assertNotIn('testpassword', body)

    def test_password_in_json(self):
        mock_request = Mock()
        mock_request.META = {DJANGO_META_CONTENT_TYPE: 'application/json; charset=UTF-8'}
        d = {'x': 'testunmasked', 'username': 'test_username', 'password': 'testpassword'}
        mock_request.body = json.dumps(d)
        mock_request.get = mock_request.META.get
        factory = RequestModelFactory(mock_request)
        body, raw_body = factory.body()
        self.assertIn('testunmasked', raw_body)
        self.assertNotIn('test_username', raw_body)
        self.assertNotIn('testpassword', raw_body)
        self.assertNotIn('test_username', body)
        self.assertNotIn('testpassword', body)

        for datum in [json.loads(body), json.loads(raw_body)]:
            self.assertEqual(datum['username'], RequestModelFactory.CLEANSED_SUBSTITUTE)
            self.assertEqual(datum['password'], RequestModelFactory.CLEANSED_SUBSTITUTE)
            self.assertEqual(datum['x'], 'testunmasked')

    def test_password_in_batched_json(self):
        mock_request = Mock()
        mock_request.META = {DJANGO_META_CONTENT_TYPE: 'application/json; charset=UTF-8'}
        d = [
            {'x': 'testunmasked', 'username': 'test_username', 'password': 'testpassword'},
            {'x': 'testunmasked', 'username': 'test_username', 'password': 'testpassword'}
        ]
        mock_request.body = json.dumps(d)
        mock_request.get = mock_request.META.get
        factory = RequestModelFactory(mock_request)
        body, raw_body = factory.body()
        self.assertIn('testunmasked', raw_body)
        self.assertNotIn('test_username', raw_body)
        self.assertNotIn('testpassword', raw_body)
        self.assertNotIn('test_username', body[0])
        self.assertNotIn('testpassword', body[0])
        self.assertNotIn('test_username', body[1])
        self.assertNotIn('testpassword', body[1])

        for data in [json.loads(body), json.loads(raw_body)]:
            for datum in data:
                self.assertEqual(datum['username'], RequestModelFactory.CLEANSED_SUBSTITUTE)
                self.assertEqual(datum['password'], RequestModelFactory.CLEANSED_SUBSTITUTE)
                self.assertEqual(datum['x'], 'testunmasked')

    def test_authorization_header(self):
        mock_request = Mock()
        mock_request.META = {'HTTP_AUTHORIZATION': 'secret'}
        mock_request.body = ''
        mock_request.get = mock_request.META.get
        factory = RequestModelFactory(mock_request)
        headers = factory.encoded_headers()
        json_headers = json.loads(headers)
        
        self.assertIn('AUTHORIZATION', json_headers)
        self.assertEqual(json_headers['AUTHORIZATION'], RequestModelFactory.CLEANSED_SUBSTITUTE)
