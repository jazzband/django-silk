import json
import logging
from unittest.mock import Mock

from django.test import TestCase

from silk.model_factory import RequestModelFactory, ResponseModelFactory

HTTP_CONTENT_TYPE = 'content-type'
JS_CONTENT = b'var x = 1;'


class TestEncodingForRequests(TestCase):
    """
    Check that the RequestModelFactory deals with encodings correctly via charset
    """

    def test_utf_plain(self):
        mock_request = Mock()
        mock_request.headers = {HTTP_CONTENT_TYPE: 'text/plain; charset=UTF-8'}
        mock_request.body = '语'
        mock_request.get = mock_request.headers.get
        factory = RequestModelFactory(mock_request)
        body, raw_body = factory.body()
        self.assertFalse(body)
        self.assertEqual(raw_body, mock_request.body)

    def test_plain(self):
        mock_request = Mock()
        mock_request.headers = {HTTP_CONTENT_TYPE: 'text/plain'}
        mock_request.body = 'sdfsdf'
        mock_request.get = mock_request.headers.get
        factory = RequestModelFactory(mock_request)
        body, raw_body = factory.body()
        self.assertFalse(body)
        self.assertEqual(raw_body, mock_request.body)

    def test_utf_json_not_encoded(self):
        mock_request = Mock()
        mock_request.headers = {HTTP_CONTENT_TYPE: 'application/json; charset=UTF-8'}
        d = {'x': '语'}
        mock_request.body = json.dumps(d)
        mock_request.get = mock_request.headers.get
        factory = RequestModelFactory(mock_request)
        body, raw_body = factory.body()
        self.assertDictEqual(json.loads(body), d)
        self.assertEqual(raw_body, mock_request.body)

    def test_utf_json_encoded(self):
        mock_request = Mock()
        mock_request.headers = {HTTP_CONTENT_TYPE: 'application/json; charset=UTF-8'}
        d = {'x': '语'}
        mock_request.body = json.dumps(d).encode('UTF-8')
        mock_request.get = mock_request.headers.get
        factory = RequestModelFactory(mock_request)
        body, raw_body = factory.body()
        self.assertDictEqual(json.loads(body), d)
        self.assertEqual(raw_body, mock_request.body.decode('UTF-8'))

    def test_utf_json_encoded_no_charset(self):
        """default to UTF-8"""
        mock_request = Mock()
        mock_request.headers = {HTTP_CONTENT_TYPE: 'application/json'}
        d = {'x': '语'}
        mock_request.body = json.dumps(d).encode('UTF-8')
        mock_request.get = mock_request.headers.get
        factory = RequestModelFactory(mock_request)
        body, raw_body = factory.body()
        self.assertDictEqual(json.loads(body), d)
        self.assertEqual(raw_body, mock_request.body.decode('UTF-8'))

    def test_invalid_encoding_json(self):
        mock_request = Mock()
        mock_request.headers = {HTTP_CONTENT_TYPE: 'application/json; charset=asdas-8'}
        d = {'x': '语'}
        mock_request.body = json.dumps(d).encode('UTF-8')
        mock_request.get = mock_request.headers.get
        factory = RequestModelFactory(mock_request)
        body, raw_body = factory.body()
        self.assertDictEqual(json.loads(body), d)
        self.assertEqual(raw_body, raw_body)


class TestEncodingForResponse(TestCase):
    """
    Check that the ResponseModelFactory deals with encodings correctly via charset
    """

    def test_utf_plain(self):
        mock = Mock()
        mock.headers = {HTTP_CONTENT_TYPE: 'text/plain; charset=UTF-8'}
        mock.content = '语'
        mock.get = mock.headers.get
        factory = ResponseModelFactory(mock)
        body, content = factory.body()
        self.assertFalse(body)
        self.assertEqual(content, mock.content)

    def test_plain(self):
        mock = Mock()
        mock.headers = {HTTP_CONTENT_TYPE: 'text/plain'}
        mock.content = 'sdfsdf'
        mock.get = mock.headers.get
        factory = ResponseModelFactory(mock)
        body, content = factory.body()
        self.assertFalse(body)
        self.assertEqual(content, mock.content)

    def test_utf_json_not_encoded(self):
        mock = Mock()
        mock.headers = {HTTP_CONTENT_TYPE: 'application/json; charset=UTF-8'}
        d = {'x': '语'}
        mock.content = json.dumps(d)
        mock.get = mock.headers.get
        factory = ResponseModelFactory(mock)
        body, content = factory.body()
        self.assertDictEqual(json.loads(body), d)
        self.assertEqual(content, mock.content)

    def test_utf_json_encoded(self):
        mock = Mock()
        mock.headers = {HTTP_CONTENT_TYPE: 'application/json; charset=UTF-8'}
        d = {'x': '语'}
        mock.content = json.dumps(d)
        mock.get = mock.headers.get
        factory = ResponseModelFactory(mock)
        body, content = factory.body()
        self.assertDictEqual(json.loads(body), d)
        self.assertEqual(content, mock.content)

    def test_utf_json_encoded_no_charset(self):
        """default to UTF-8"""
        mock = Mock()
        mock.headers = {HTTP_CONTENT_TYPE: 'application/json'}
        d = {'x': '语'}
        mock.content = json.dumps(d)
        mock.get = mock.headers.get
        factory = ResponseModelFactory(mock)
        body, content = factory.body()
        self.assertDictEqual(json.loads(body), d)
        self.assertEqual(content, mock.content)

    def test_invalid_encoding_json(self):
        mock = Mock()
        mock.headers = {HTTP_CONTENT_TYPE: 'application/json; charset=asdas-8'}
        d = {'x': '语'}
        mock.content = json.dumps(d)
        mock.get = mock.headers.get
        factory = ResponseModelFactory(mock)
        body, content = factory.body()
        self.assertDictEqual(json.loads(body), d)
        self.assertEqual(mock.content, content)


class TestJavaScriptContentTypeResponse(TestCase):
    """Responses with JavaScript content types should not log warnings when
    the content cannot be parsed as JSON (issue #374)."""

    def _make_response(self, content_type, content):
        mock = Mock()
        mock.headers = {HTTP_CONTENT_TYPE: content_type}
        mock.content = content
        mock.get = mock.headers.get
        return mock

    def test_application_javascript_no_warning(self):
        mock = self._make_response('application/javascript', JS_CONTENT)
        factory = ResponseModelFactory(mock)
        with self.assertNoLogs('silk.model_factory', level=logging.WARNING):
            body, content = factory.body()
        self.assertFalse(body)

    def test_text_javascript_no_warning(self):
        mock = self._make_response('text/javascript', JS_CONTENT)
        factory = ResponseModelFactory(mock)
        with self.assertNoLogs('silk.model_factory', level=logging.WARNING):
            body, content = factory.body()
        self.assertFalse(body)

    def test_application_x_javascript_no_warning(self):
        mock = self._make_response('application/x-javascript', JS_CONTENT)
        factory = ResponseModelFactory(mock)
        with self.assertNoLogs('silk.model_factory', level=logging.WARNING):
            body, content = factory.body()
        self.assertFalse(body)

    def test_text_x_javascript_no_warning(self):
        mock = self._make_response('text/x-javascript', JS_CONTENT)
        factory = ResponseModelFactory(mock)
        with self.assertNoLogs('silk.model_factory', level=logging.WARNING):
            body, content = factory.body()
        self.assertFalse(body)

    def test_json_content_type_warns_on_invalid_json(self):
        mock = self._make_response('application/json', JS_CONTENT)
        factory = ResponseModelFactory(mock)
        with self.assertLogs('silk.model_factory', level=logging.WARNING):
            body, content = factory.body()
        self.assertFalse(body)

    def test_javascript_with_valid_json_parses(self):
        d = {'asdf': 'qwer'}
        mock = self._make_response('application/javascript', json.dumps(d).encode())
        factory = ResponseModelFactory(mock)
        body, content = factory.body()
        self.assertDictEqual(json.loads(body), d)


class TestJavaScriptContentTypeRequest(TestCase):
    """Requests with JavaScript content types should silently fall back
    when the body cannot be parsed as JSON."""

    def _make_request(self, content_type, body):
        mock = Mock()
        mock.headers = {HTTP_CONTENT_TYPE: content_type}
        mock.body = body
        mock.GET = {}
        mock.path = '/test/'
        mock.path_info = '/test/'
        mock.method = 'POST'
        mock.get = mock.headers.get
        return mock

    def test_application_javascript_no_warning(self):
        mock = self._make_request('application/javascript', JS_CONTENT)
        factory = RequestModelFactory(mock)
        with self.assertNoLogs('silk.model_factory', level=logging.WARNING):
            body, raw_body = factory.body()
        self.assertEqual(body, JS_CONTENT.decode('UTF-8'))

    def test_javascript_with_valid_json_parses(self):
        d = {'asdf': 'qwer'}
        mock = self._make_request('application/javascript', json.dumps(d).encode())
        factory = RequestModelFactory(mock)
        body, raw_body = factory.body()
        self.assertDictEqual(json.loads(body), d)
