import os
import random
from unittest.mock import patch

from django.conf import settings
from django.test import TestCase

from silk.config import SilkyConfig
from silk.middleware import silky_reverse
from silk.views.sql_detail import SQLDetailView

from .test_lib.mock_suite import MockSuite


class TestViewSQLDetail(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        SilkyConfig().SILKY_AUTHENTICATION = False
        SilkyConfig().SILKY_AUTHORISATION = False

    def test_allowed_file_paths_nothing_specified(self):
        """by default we dont display any source, and it should return correctly"""
        request = MockSuite().mock_request()
        query = MockSuite().mock_sql_queries(request=request, n=1)[0]
        response = self.client.get(
            silky_reverse(
                "request_sql_detail",
                kwargs={"sql_id": query.id, "request_id": request.id},
            )
        )
        self.assertTrue(response.status_code == 200)

    def test_allowed_file_paths_available_source(self):
        """if we request to view source that exists in the TB all should be fine"""
        request = MockSuite().mock_request()
        query = MockSuite().mock_sql_queries(request=request, n=1)[0]
        tb = query.traceback_ln_only
        _, files = SQLDetailView()._urlify(tb)
        file_path = random.choice(files)
        with open(file_path) as f:
            line_num = random.randint(0, len(f.read().split("\n")))
        response = self.client.get(
            silky_reverse(
                "request_sql_detail",
                kwargs={"sql_id": query.id, "request_id": request.id},
            ),
            data={"line_num": line_num, "file_path": file_path},
        )
        self.assertTrue(response.status_code == 200)

    def test_allowed_file_paths_unavailable_source(self):
        """if we request to view source that is not in the traceback we should get a 403"""
        request = MockSuite().mock_request()
        query = MockSuite().mock_sql_queries(request=request, n=1)[0]
        file_path = settings.TEMP_DIR + "/blah"
        with open(file_path, "w") as f:
            f.write("test")
        response = self.client.get(
            silky_reverse(
                "request_sql_detail",
                kwargs={"sql_id": query.id, "request_id": request.id},
            ),
            data={"line_num": 0, "file_path": file_path},
        )
        self.assertTrue(response.status_code == 403)

    def test_virtualenv_not_available_no_highlight(self):
        """if we don't have a virtualenv, there should be no code hightlighted"""
        request = MockSuite().mock_request()
        query = MockSuite().mock_sql_queries(request=request)[0]
        url = silky_reverse(
            "request_sql_detail", kwargs={"sql_id": query.id, "request_id": request.id}
        )
        with patch.dict(os.environ, {}, clear=True):
            self.assertIsNone(os.environ.get("VIRTUAL_ENV"))
            response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, " is-third-party")
        self.assertNotContains(response, " not-third-party")

    def test_virtualenv_hightlight(self):
        """if we have a virtualenv, there should be code hightlighted"""
        request = MockSuite().mock_request()
        query = MockSuite().mock_sql_queries(request=request)[0]
        url = silky_reverse(
            "request_sql_detail", kwargs={"sql_id": query.id, "request_id": request.id}
        )
        with patch.dict(
            os.environ,
            {"VIRTUAL_ENV": "/some/virtualenv/that/doesnt/really/exist"},
            clear=True,
        ):
            response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, " not-third-party")
