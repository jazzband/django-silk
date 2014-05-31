import random

from django.test import TestCase
from mock import Mock

from silk.tests.test_lib.mock_suite import MockSuite
from silk.views.root import RootView


class TestRootViewDefaults(TestCase):
    def test_path(self):
        requests = [MockSuite().mock_request() for _ in range(0, 3)]
        paths = RootView()._get_paths()
        for r in requests:
            self.assertIn(r.path, paths)
        self.assertIn('', paths)

    def test_show(self):
        self.assertIn(RootView.default_show, RootView.show)

    def test_order_by(self):
        self.assertIn(RootView.defualt_order_by, RootView.order_by)


class TestContext(TestCase):
    def test_default(self):
        request = Mock(spec_set=['GET'])
        request.GET = {}
        context = RootView()._create_context(request)
        self.assertDictContainsSubset({
                                          'show': RootView.default_show,
                                          'order_by': RootView.defualt_order_by,
                                          'options_show': RootView.show,
                                          'options_order_by': RootView.order_by,
                                          'options_paths': RootView()._get_paths()
                                      }, context)
        self.assertNotIn('path', context)
        self.assertIn('results', context)

    def test_get(self):
        request = Mock(spec_set=['GET'])
        show = 10
        path = '/path/to/somewhere/'
        order_by = 'Path'
        request.GET = {'show': show,
                       'path': path,
                       'order_by': order_by}
        context = RootView()._create_context(request)
        self.assertDictContainsSubset({
                                          'show': show,
                                          'order_by': order_by,
                                          'path': path,
                                          'options_show': RootView.show,
                                          'options_order_by': RootView.order_by,
                                          'options_paths': RootView()._get_paths()
                                      }, context)
        self.assertIn('results', context)


class TestGetObjects(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.requests = [MockSuite().mock_request() for _ in range(0, 50)]

    def test_defaults(self):
        objects = RootView()._get_objects()
        self.assertEqual(len(objects), 25)
        self.assertSorted(objects, 'start_time')

    def assertSorted(self, objects, sort_field):
        for idx, r in enumerate(objects):
            try:
                nxt = objects[idx + 1]
                self.assertGreaterEqual(getattr(r, sort_field), getattr(nxt, sort_field))
            except IndexError:
                pass

    def test_ordering(self):
        self.assertSorted(objects=RootView()._get_objects(order_by='Time'),
                          sort_field='start_time')
        self.assertSorted(objects=RootView()._get_objects(order_by='Path'),
                          sort_field='path')
        self.assertSorted(objects=RootView()._get_objects(order_by='Num. DB Queries'),
                          sort_field='num_sql_queries')
        self.assertSorted(objects=RootView()._get_objects(order_by='Time Spent Overall'),
                          sort_field='total_time')
        self.assertSorted(objects=RootView()._get_objects(order_by='Time Spent DB'),
                          sort_field='total_db_time')

    def test_show(self):
        objects = RootView()._get_objects(show=10)
        self.assertEqual(len(objects), 10)

    def test_path(self):
        request = random.choice(self.requests)
        objects = RootView()._get_objects(path=request.path)
        for r in objects:
            self.assertEqual(r.path, request.path)

    def test_time_spent_db_with_path(self):
        request = random.choice(self.requests)
        query_set = RootView()._get_objects(order_by='Time Spent DB',
                                            path=request.path)
        num_results = len(query_set)
        self.assertTrue(num_results)
        for result in query_set:
            self.assertEqual(result.path, request.path)
