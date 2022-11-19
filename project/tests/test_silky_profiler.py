from time import sleep

from django.test import TestCase

from silk.collector import DataCollector
from silk.models import Request, _time_taken
from silk.profiling.profiler import silk_profile

from .test_lib.mock_suite import MockSuite


class TestProfilerRequests(TestCase):
    def test_context_manager_no_request(self):
        DataCollector().configure()
        with silk_profile(name='test_profile'):
            sleep(0.1)
        self.assertFalse(DataCollector().profiles)

    def test_decorator_no_request(self):
        DataCollector().configure()

        @silk_profile()
        def func():
            sleep(0.1)

        func()
        profile = list(DataCollector().profiles.values())[0]
        self.assertFalse(profile['request'])

    def test_context_manager_request(self):
        DataCollector().configure(Request.objects.create(path='/to/somewhere'))
        with silk_profile(name='test_profile'):
            sleep(0.1)
        profile = list(DataCollector().profiles.values())[0]
        self.assertEqual(DataCollector().request, profile['request'])

    def test_decorator_request(self):
        DataCollector().configure(Request.objects.create(path='/to/somewhere'))

        @silk_profile()
        def func():
            sleep(0.1)

        func()
        profile = list(DataCollector().profiles.values())[0]
        self.assertEqual(DataCollector().request, profile['request'])


class TestProfilertContextManager(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        r = Request.objects.create()
        DataCollector().configure(r)
        with silk_profile(name='test_profile'):
            sleep(0.1)

    def test_one_object(self):
        self.assertEqual(len(DataCollector().profiles), 1)

    def test_name(self):
        profile = list(DataCollector().profiles.values())[0]
        self.assertEqual(profile['name'], 'test_profile')

    def test_time_taken(self):
        profile = list(DataCollector().profiles.values())[0]
        time_taken = _time_taken(start_time=profile['start_time'], end_time=profile['end_time'])
        self.assertGreaterEqual(time_taken, 100)
        self.assertLess(time_taken, 110)


class TestProfilerDecorator(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        DataCollector().configure(Request.objects.create())

        @silk_profile()
        def func():
            sleep(0.1)

        func()

    def test_one_object(self):
        self.assertEqual(len(DataCollector().profiles), 1)

    def test_name(self):
        profile = list(DataCollector().profiles.values())[0]
        self.assertEqual(profile['name'], 'func')

    def test_time_taken(self):
        profile = list(DataCollector().profiles.values())[0]
        time_taken = _time_taken(start_time=profile['start_time'], end_time=profile['end_time'])
        self.assertGreaterEqual(time_taken, 100)
        self.assertLess(time_taken, 115)


class TestQueries(TestCase):
    def test_no_queries_before(self):
        DataCollector().configure(Request.objects.create())
        with silk_profile(name='test_no_queries_before_profile'):
            mock_queries = MockSuite().mock_sql_queries(n=5, as_dict=True)
            DataCollector().register_query(*mock_queries)
        profile = list(DataCollector().profiles.values())[0]
        self.assertEqual(profile['name'], 'test_no_queries_before_profile')
        queries = profile['queries']
        self.assertEqual(len(queries), 5)
        for query in DataCollector().queries:
            self.assertIn(query, queries)

    def test_queries_before(self):
        """test that any queries registered before profiling begins are ignored"""
        DataCollector().configure(Request.objects.create())
        DataCollector().register_query(*MockSuite().mock_sql_queries(n=2, as_dict=True))
        before = [x for x in DataCollector().queries]
        with silk_profile(name='test_no_queries_before_profile'):
            mock_queries = MockSuite().mock_sql_queries(n=5, as_dict=True)
            DataCollector().register_query(*mock_queries)
        profile = list(DataCollector().profiles.values())[0]
        self.assertEqual(profile['name'], 'test_no_queries_before_profile')
        queries = profile['queries']
        self.assertEqual(len(queries), 5)
        for query in set(DataCollector().queries).difference(before):
            self.assertIn(query, queries)
