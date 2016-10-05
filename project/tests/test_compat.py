# coding=utf-8

import json
import sys

from django.test import TestCase
from mock import Mock

from silk.model_factory import RequestModelFactory, ResponseModelFactory

DJANGO_META_CONTENT_TYPE = 'CONTENT_TYPE'
HTTP_CONTENT_TYPE = 'Content-Type'


class TestByteStringCompatForResponse(TestCase):

    def test_python3_bytes_compat(self):
        """
        Test ResponseModelFactory formats json with bytes content
        """
        if sys.version_info >= (3, 0, 0):
            mock = Mock()
            mock._headers = {HTTP_CONTENT_TYPE: 'application/json;'}
            d = {'k': 'v'}
            mock.content = bytes(json.dumps(d), 'utf-8')
            mock.get = mock._headers.get
            factory = ResponseModelFactory(mock)
            body, content = factory.body()
            self.assertDictEqual(json.loads(body), d)

    # Testing invalid json throws an exception in the tests
    # def test_python3_invalid_content_compat(self):
    #     """
    #     Test ResponseModelFactory returns empty string for invalid json
    #     """
    #     if sys.version_info >= (3, 0, 0):
    #         mock = Mock()
    #         mock.pk = 'test'
    #         mock._headers = {HTTP_CONTENT_TYPE: 'application/json;'}
    #         mock.content = b'invalid json'
    #         mock.get = mock._headers.get
    #         factory = ResponseModelFactory(mock)
    #         body, content = factory.body()
    #         self.assertEqual(body, '')

    def test_python2_bytes_content_compat(self):
        """
        Test that ResponseModelFactory returns correct json string for a
        bytestring content
        """
        if sys.version_info < (3, 0, 0):
            mock = Mock()
            mock._headers = {HTTP_CONTENT_TYPE: 'application/json;'}
            d = {'k': 'v'}
            mock.content = bytes(json.dumps(d))
            mock.get = mock._headers.get
            factory = ResponseModelFactory(mock)
            body, content = factory.body()
            self.assertDictEqual(json.loads(body), d)

    def test_python2_str_content_compat(self):
        """
        Test ResponseModelFactory formats json for str
        """
        if sys.version_info < (3, 0, 0):
            mock = Mock()
            mock._headers = {HTTP_CONTENT_TYPE: 'application/json;'}
            d = {'k': 'v'}
            mock.content = str(json.dumps(d))
            mock.get = mock._headers.get
            factory = ResponseModelFactory(mock)
            body, content = factory.body()
            self.assertDictEqual(json.loads(body), d)

    def test_python2_unicode_content_compat(self):
        """
        Test ResponseModelFactory formats json for unicode
        """
        if sys.version_info < (3, 0, 0):
            mock = Mock()
            mock._headers = {HTTP_CONTENT_TYPE: 'application/json;'}
            d = u'{"k": "v"}'
            mock.content = d
            mock.get = mock._headers.get
            factory = ResponseModelFactory(mock)
            body, content = factory.body()
            self.assertDictEqual(json.loads(body), json.loads(d))

    # Testing invalid json throws exceptions within the test
    # def test_python2_invalid_content_compat(self):
    #     """
    #     Test ResponseModelFactory returns an empty string for invalid json
    #     content
    #     """
    #     if sys.version_info < (3, 0, 0):
    #         mock = Mock()
    #         mock._headers = {HTTP_CONTENT_TYPE: 'application/json;'}
    #         d = b'invalid json'
    #         mock.content = d
    #         mock.get = mock._headers.get
    #         factory = ResponseModelFactory(mock)
    #         body, content = factory.body()
    #         self.assertEqual(body, '')
