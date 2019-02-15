import random
import unittest

from django.test import TestCase
from mock import Mock

from .test_lib.mock_suite import MockSuite
from silk.views.requests import RequestsView


class TestRootViewDefaults(TestCase):
    def test_path(self):
        requests = [MockSuite().mock_request() for _ in range(0, 3)]
        paths = RequestsView()._get_paths()
        for r in requests:
            self.assertIn(r.path, paths)

    def test_show(self):
        self.assertIn(RequestsView.default_show, RequestsView.show)

    def test_order_by(self):
        self.assertIn(RequestsView.default_order_by, RequestsView.order_by)


class TestContext(TestCase):
    def test_default(self):
        request = Mock(spec_set=['GET', 'session'])
        request.session = {}
        request.GET = {}
        context = RequestsView()._create_context(request)
        self.assertDictContainsSubset({
                                          'show': RequestsView.default_show,
                                          'order_by': RequestsView.default_order_by,
                                          'options_show': RequestsView.show,
                                          'options_order_by': RequestsView().options_order_by,
                                          'options_order_dir': RequestsView().options_order_dir,
                                      }, context)
        self.assertQuerysetEqual(context['options_paths'], RequestsView()._get_paths())
        self.assertNotIn('path', context)
        self.assertIn('results', context)

    def test_get(self):
        request = Mock(spec_set=['GET', 'session'])
        request.session = {}
        show = 10
        path = '/path/to/somewhere/'
        order_by = 'path'
        request.GET = {'show': show,
                       'path': path,
                       'order_by': order_by}
        context = RequestsView()._create_context(request)
        self.assertDictContainsSubset({
                                          'show': show,
                                          'order_by': order_by,
                                          'path': path,
                                          'options_show': RequestsView.show,
                                          'options_order_by': RequestsView().options_order_by,
                                          'options_order_dir': RequestsView().options_order_dir,
                                      }, context)
        self.assertQuerysetEqual(context['options_paths'], RequestsView()._get_paths())
        self.assertIn('results', context)


class TestGetObjects(TestCase):
    def assertSorted(self, objects, sort_field):
        for idx, r in enumerate(objects):
            try:
                nxt = objects[idx + 1]
                self.assertGreaterEqual(getattr(r, sort_field), getattr(nxt, sort_field))
            except IndexError:
                pass

    @classmethod
    def setUpClass(cls):
        super(TestGetObjects, cls).setUpClass()
        cls.requests = [MockSuite().mock_request() for _ in range(0, 50)]

    def test_defaults(self):
        objects = RequestsView()._get_objects()
        self.assertEqual(len(objects), 25)
        self.assertSorted(objects, 'start_time')

    def test_show(self):
        objects = RequestsView()._get_objects(show=10)
        self.assertEqual(len(objects), 10)

    def test_path(self):
        request = random.choice(self.requests)
        objects = RequestsView()._get_objects(path=request.path)
        for r in objects:
            self.assertEqual(r.path, request.path)

    @unittest.skip("Flaky")
    def test_time_spent_db_with_path(self):
        request = random.choice(self.requests)
        query_set = RequestsView()._get_objects(order_by='db_time',
                                                path=request.path)
        num_results = query_set.count()
        self.assertTrue(num_results)
        for result in query_set:
            self.assertEqual(result.path, request.path)


class TestOrderingRequestView(TestCase):
    def assertSorted(self, objects, sort_field):
        for idx, r in enumerate(objects):
            try:
                nxt = objects[idx + 1]
                self.assertGreaterEqual(getattr(r, sort_field), getattr(nxt, sort_field))
            except IndexError:
                pass

    def test_ordering(self):
        self.assertSorted(objects=RequestsView()._get_objects(order_by='start_time'),
                          sort_field='start_time')
        self.assertSorted(objects=RequestsView()._get_objects(order_by='path'),
                          sort_field='path')
        self.assertSorted(objects=RequestsView()._get_objects(order_by='num_sql_queries'),
                          sort_field='num_sql_queries')
        self.assertSorted(objects=RequestsView()._get_objects(order_by='time_taken'),
                          sort_field='time_taken')
        self.assertSorted(objects=RequestsView()._get_objects(order_by='db_time'),
                          sort_field='db_time')

