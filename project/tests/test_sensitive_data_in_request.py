# coding=utf-8

import json

from django.test import TestCase
from unittest.mock import Mock

from silk.model_factory import RequestModelFactory, ResponseModelFactory

DJANGO_META_CONTENT_TYPE = 'CONTENT_TYPE'
HTTP_CONTENT_TYPE = 'Content-Type'
CLEANSED = RequestModelFactory.CLEANSED_SUBSTITUTE


class MaskCredentialsInFormsTest(TestCase):
    def _mask(self, value):
        return RequestModelFactory(None)._mask_credentials(value)

    def test_mask_credentials_preserves_single_insensitive_values(self):
        body = "foo=public"
        expected = "foo=public"
        self.assertEqual(expected, self._mask(body))

    def test_mask_credentials_masks_sensitive_values(self):
        body = "password=secret"
        expected = "password={}".format(CLEANSED)
        self.assertEqual(expected, self._mask(body))

    def test_mask_credentials_masks_multiple_sensitive_values(self):
        body = "password=mypassword&secret=mysecret"
        expected = "password={}&secret={}".format(CLEANSED, CLEANSED)
        self.assertEqual(expected, self._mask(body))

    def test_mask_credentials_masks_sensitive_values_between_insensitive_values(self):
        body = "public1=foo&password=secret&public2=bar"
        expected = "public1=foo&password={}&public2=bar".format(CLEANSED)
        self.assertEqual(expected, self._mask(body))

    def test_mask_credentials_preserves_insensitive_values_between_sensitive_values(self):
        body = "password=1&foo=public&secret=2"
        expected = "password={}&foo=public&secret={}".format(CLEANSED, CLEANSED)
        self.assertEqual(expected, self._mask(body))

    def test_mask_credentials_is_case_insensitive(self):
        body = "UsErNaMe=secret"
        expected = "UsErNaMe={}".format(CLEANSED)
        self.assertEqual(expected, self._mask(body))

    def test_mask_credentials_handles_prefixes(self):
        body = "prefixed-username=secret"
        expected = "prefixed-username={}".format(CLEANSED)
        self.assertEqual(expected, self._mask(body))

    def test_mask_credentials_handles_suffixes(self):
        body = "username-with-suffix=secret"
        expected = "username-with-suffix={}".format(CLEANSED)
        self.assertEqual(expected, self._mask(body))

    def test_mask_credentials_handles_regex_characters(self):
        body = "password=secret++"
        expected = "password={}".format(CLEANSED)
        self.assertEqual(expected, self._mask(body))

    def test_mask_credentials_handles_complex_cases(self):
        body = "foo=public&prefixed-uSeRname-with-suffix=secret&bar=public"
        expected = "foo=public&prefixed-uSeRname-with-suffix={}&bar=public".format(CLEANSED)
        self.assertEqual(expected, self._mask(body))


class MaskCredentialsInJsonTest(TestCase):
    def _mask(self, value):
        return RequestModelFactory(None)._mask_credentials(json.dumps(value))

    def test_mask_credentials_preserves_single_insensitive_values(self):
        self.assertIn("public", self._mask({"foo": "public"}))

    def test_mask_credentials_preserves_insensitive_values_in_presence_of_sensitive(self):
        self.assertIn("public", self._mask({"password": "secret", "foo": "public"}))

    def test_mask_credentials_masks_sensitive_values(self):
        self.assertNotIn("secret", self._mask({"password": "secret"}))

    def test_mask_credentials_masks_sensitive_values_in_presence_of_regular(self):
        self.assertNotIn("secret", self._mask({"foo": "public", "password": "secret"}))

    def test_mask_credentials_is_case_insensitive(self):
        self.assertNotIn("secret", self._mask({"UsErNaMe": "secret"}))

    def test_mask_credentials_handles_prefixes(self):
        self.assertNotIn("secret", self._mask({"prefixed-username": "secret"}))

    def test_mask_credentials_handles_suffixes(self):
        self.assertNotIn("secret", self._mask({"username-with-suffix": "secret"}))

    def test_mask_credentials_handles_complex_cases(self):
        self.assertNotIn("secret", self._mask({
            "foo": "public",
            "prefixed-uSeRname-with-suffix": "secret"
        }))

    def test_mask_credentials_in_nested_data_structures(self):
        self.assertNotIn("secret", self._mask({
            "foo": "public",
            "nested": {
                "prefixed-uSeRname-with-suffix": "secret",
            },
        }))



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
        d = {'x': 'testunmasked', 'username': 'test_username', 'password': 'testpassword',
             'prefixed-secret': 'testsecret'}
        mock_request.body = json.dumps(d)
        mock_request.get = mock_request.META.get
        factory = RequestModelFactory(mock_request)
        body, raw_body = factory.body()
        self.assertIn('testunmasked', raw_body)
        self.assertNotIn('test_username', raw_body)
        self.assertNotIn('testpassword', raw_body)
        self.assertNotIn('testsecret', raw_body)
        self.assertNotIn('test_username', body)
        self.assertNotIn('testpassword', body)
        self.assertNotIn('testsecret', body)

        for datum in [json.loads(body), json.loads(raw_body)]:
            self.assertEqual(datum['username'], RequestModelFactory.CLEANSED_SUBSTITUTE)
            self.assertEqual(datum['password'], RequestModelFactory.CLEANSED_SUBSTITUTE)
            self.assertEqual(datum['prefixed-secret'], RequestModelFactory.CLEANSED_SUBSTITUTE)
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
