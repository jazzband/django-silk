from unittest import mock

from django.db import connection, connections
from django.test import TestCase
from django.test.utils import CaptureQueriesContext

from silk.models import Request
from silk.utils.data_deletion import delete_model

from .factories import RequestMinFactory, ResponseFactory


class TestDeleteModel(TestCase):
    def test_delete_model_removes_all_rows(self):
        for _ in range(5):
            RequestMinFactory.create()
        self.assertEqual(Request.objects.count(), 5)

        delete_model(Request)

        self.assertEqual(Request.objects.count(), 0)

    def test_delete_model_respects_constrained_max_query_params(self):
        """
        Regression test for
        https://github.com/jazzband/django-silk/issues/421

        delete_model() previously used a hardcoded batch size (800)
        regardless of the database backend's actual query parameter
        limit. That limit varies across SQLite builds/versions (and is
        exposed to Django as connection.features.max_query_params), so
        a hardcoded batch size that happens to work in one environment
        can still exceed a more constrained build's real limit
        elsewhere, raising "too many SQL variables". Every DELETE
        statement issued -- including cascade deletes on related
        tables -- must never use more parameters than the backend's
        actual limit allows.
        """
        for _ in range(30):
            ResponseFactory.create()
        self.assertEqual(Request.objects.count(), 30)

        with mock.patch.object(
            connections["default"].features.__class__,
            "max_query_params",
            5,
        ):
            with CaptureQueriesContext(connection) as ctx:
                delete_model(Request)

        self.assertEqual(Request.objects.count(), 0)

        max_params_seen = 0
        for query in ctx.captured_queries:
            sql = query["sql"]
            if "DELETE" not in sql.upper():
                continue
            start = sql.find("IN (")
            if start == -1:
                continue
            end = sql.find(")", start)
            param_count = sql[start + 4:end].count(",") + 1
            max_params_seen = max(max_params_seen, param_count)

        self.assertLessEqual(
            max_params_seen,
            5,
            "a DELETE query used more parameters than the constrained "
            "max_query_params limit allows",
        )
