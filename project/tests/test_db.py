"""
Test profiling of DB queries without mocking, to catch possible
incompatibility
"""

from django.shortcuts import reverse
from django.test import Client, TestCase

from silk.collector import DataCollector
from silk.config import SilkyConfig
from silk.models import Request
from silk.profiling.profiler import silk_profile

from .factories import BlindFactory


class TestDbQueries(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        BlindFactory.create_batch(size=5)
        SilkyConfig().SILKY_META = False

    def setUp(self):
        DataCollector().clear()

    def test_profile_request_to_db(self):
        DataCollector().configure(Request(reverse('example_app:index')))

        with silk_profile(name='test_profile'):
            resp = self.client.get(reverse('example_app:index'))

        self.assertEqual(len(DataCollector().queries), 1, [q['query'] for q in DataCollector().queries.values()])
        self.assertEqual(len(resp.context['blinds']), 5)

    def test_profile_request_to_db_with_constraints(self):
        DataCollector().configure(Request(reverse('example_app:create')))

        resp = self.client.post(reverse('example_app:create'), {'name': 'Foo'})
        self.assertTrue(len(DataCollector().queries))
        self.assertTrue(list(DataCollector().queries.values())[-1]['query'].startswith('INSERT'))
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
        SilkyConfig().SILKY_ANALYZE_QUERIES = False

    def test_analyze_queries(self):
        DataCollector().configure(Request(reverse('example_app:index')))
        client = Client()

        with silk_profile(name='test_profile'):
            resp = client.get(reverse('example_app:index'))

        DataCollector().profiles.values()
        assert len(resp.context['blinds']) == 5
