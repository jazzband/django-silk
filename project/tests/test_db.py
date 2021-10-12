"""
Test profiling of DB queries without mocking, to catch possible
incompatibility
"""
from django.test import Client, TestCase
from django.urls import reverse

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

    def test_profile_request_to_db(self):
        client = Client()
        DataCollector().configure(Request(reverse('example_app:index')))

        with silk_profile(name='test_profile'):
            resp = client.get(reverse('example_app:index'))

        DataCollector().profiles.values()
        assert len(resp.context["blinds"]) == 5


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
        assert len(resp.context["blinds"]) == 5
