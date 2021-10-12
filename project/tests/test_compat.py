import json
from unittest.mock import Mock

from django.test import TestCase

from silk.model_factory import ResponseModelFactory

DJANGO_META_CONTENT_TYPE = "CONTENT_TYPE"
HTTP_CONTENT_TYPE = "Content-Type"


class TestByteStringCompatForResponse(TestCase):
    def test_bytes_compat(self):
        """
        Test ResponseModelFactory formats json with bytes content
        """
        mock = Mock()
        mock.headers = {HTTP_CONTENT_TYPE: "application/json;"}
        d = {"k": "v"}
        mock.content = bytes(json.dumps(d), "utf-8")
        mock.get = mock.headers.get
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
