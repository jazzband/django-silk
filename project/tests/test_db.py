"""
Test profiling of DB queries without mocking, to catch possible
incompatibility
"""
from django.db import IntegrityError, transaction
from django.db.models.sql.compiler import SQLCompiler
from django.shortcuts import reverse
from django.test import Client, TestCase
from example_app.models import Blind

from silk.collector import DataCollector
from silk.config import SilkyConfig
from silk.models import Request
from silk.profiling.profiler import silk_profile
from silk.sql import execute_sql

from .factories import BlindFactory


class TestDbQueries(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        BlindFactory.create_batch(size=5)
        SilkyConfig().SILKY_META = False

    def test_profile_request_to_db(self):
        DataCollector().configure(Request(reverse('example_app:index')))

        with silk_profile(name='test_profile'):
            resp = self.client.get(reverse('example_app:index'))

        DataCollector().profiles.values()
        assert len(resp.context['blinds']) == 5

    def test_profile_request_to_db_with_constraints(self):
        DataCollector().configure(Request(reverse('example_app:create')))

        resp = self.client.post(reverse('example_app:create'), {'name': 'Foo'})
        self.assertEqual(resp.status_code, 302)


class TestAnalyzeQueries(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        BlindFactory.create_batch(size=5)
        SilkyConfig().SILKY_META = False
        SilkyConfig().SILKY_ANALYZE_QUERIES = True

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        SilkyConfig().SILKLY_ANALYZE_QUERIES = False

    def test_analyze_queries(self):
        DataCollector().configure(Request(reverse('example_app:index')))
        client = Client()

        with silk_profile(name='test_profile'):
            resp = client.get(reverse('example_app:index'))

        DataCollector().profiles.values()
        assert len(resp.context['blinds']) == 5


class TestAnalyzeQueriesExplainParams(TestAnalyzeQueries):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        SilkyConfig().SILKY_EXPLAIN_FLAGS = {'verbose': True}

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        SilkyConfig().SILKY_EXPLAIN_FLAGS = None


class TestFailedQueryInTransaction(TestCase):
    """The query's own error must reach the caller, not one from silk's EXPLAIN (#672)"""

    def setUp(self):
        # Wrap queries the same way SilkyMiddleware.process_request does
        if not hasattr(SQLCompiler, '_execute_sql'):
            SQLCompiler._execute_sql = SQLCompiler.execute_sql
            SQLCompiler.execute_sql = execute_sql
        DataCollector().configure(Request(path='/path/to/somewhere'), should_profile=False)

    def test_failed_update_raises_integrity_error(self):
        first = Blind.objects.create(name='first')
        second = Blind.objects.create(name='second')
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                # A duplicate primary key fails on every database backend
                Blind.objects.filter(id=second.id).update(id=first.id)
