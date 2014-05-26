from time import sleep

from django.test import TestCase
from silky.collector import DataCollector

from silky.models import Profile, Request
from silky.profiling.profiler import silky_profile
from silky.tests.lib.mock_suite import MockSuite


class TestProfilerRequests(TestCase):
    def test_context_manager_no_request(self):
        DataCollector().request = None
        Profile.objects.all().delete()
        with silky_profile(name='test_profile'):
            sleep(0.1)
        profile = Profile.objects.all()[0]
        self.assertFalse(profile.request)

    def test_decorator_no_request(self):
        DataCollector().request = None
        Profile.objects.all().delete()

        @silky_profile()
        def func():
            sleep(0.1)

        func()
        profile = Profile.objects.all()[0]
        self.assertFalse(profile.request)

    def test_context_manager_request(self):
        DataCollector().request = Request.objects.create(path='/to/somewhere')
        Profile.objects.all().delete()
        with silky_profile(name='test_profile'):
            sleep(0.1)
        profile = Profile.objects.all()[0]
        self.assertEqual(DataCollector().request, profile.request)

    def test_decorator_request(self):
        DataCollector().request = Request.objects.create(path='/to/somewhere')
        Profile.objects.all().delete()

        @silky_profile()
        def func():
            sleep(0.1)

        func()
        profile = Profile.objects.all()[0]
        self.assertEqual(DataCollector().request, profile.request)


class TestProfilertContextManager(TestCase):
    @classmethod
    def setUpClass(cls):
        Profile.objects.all().delete()
        with silky_profile(name='test_profile'):
            sleep(0.1)

    def test_one_object(self):
        self.assertTrue(Profile.objects.count(), 1)

    def test_name(self):
        profile = Profile.objects.all()[0]
        self.assertEqual(profile.name, 'test_profile')

    def test_time_taken(self):
        profile = Profile.objects.all()[0]
        self.assertGreaterEqual(profile.time_taken, 100)
        self.assertLess(profile.time_taken, 110)


class TestProfilerDecorator(TestCase):
    @classmethod
    def setUpClass(cls):
        Profile.objects.all().delete()

        @silky_profile()
        def func():
            sleep(0.1)

        func()

    def test_one_object(self):
        self.assertTrue(Profile.objects.count(), 1)

    def test_name(self):
        profile = Profile.objects.all()[0]
        self.assertEqual(profile.name, 'func')

    def test_time_taken(self):
        profile = Profile.objects.all()[0]
        self.assertGreaterEqual(profile.time_taken, 100)
        self.assertLess(profile.time_taken, 110)


class TestQueries(TestCase):
    def test_no_queries_before(self):
        DataCollector().clear()
        Profile.objects.all().delete()
        with silky_profile(name='test_no_queries_before_profile'):
            mock_queries = MockSuite().mock_sql_queries(n=5)
            DataCollector().register_query(*mock_queries)
        profile = Profile.objects.all()[0]
        self.assertEqual(profile.name, 'test_no_queries_before_profile')
        queries = profile.queries.all()
        self.assertEqual(len(queries), 5)
        for query in mock_queries:
            self.assertIn(query, queries)

    def test_queries_before(self):
        """test that any queries registered before profiling begins are ignored"""
        DataCollector().clear()
        DataCollector().register_query(*MockSuite().mock_sql_queries(n=2))
        Profile.objects.all().delete()
        with silky_profile(name='test_no_queries_before_profile'):
            mock_queries = MockSuite().mock_sql_queries(n=5)
            DataCollector().register_query(*mock_queries)
        profile = Profile.objects.all()[0]
        self.assertEqual(profile.name, 'test_no_queries_before_profile')
        queries = profile.queries.all()
        self.assertEqual(len(queries), 5)
        for query in mock_queries:
            self.assertIn(query, queries)