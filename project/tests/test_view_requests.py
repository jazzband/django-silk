import random
import unittest
from unittest.mock import Mock

from django.test import TestCase
from django.utils import timezone as django_timezone

from silk import models
from silk.middleware import silky_reverse
from silk.views.requests import RequestsView

from .test_lib.assertion import dict_contains
from .test_lib.mock_suite import MockSuite


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
        self.assertTrue(dict_contains({
            'show': RequestsView.default_show,
            'order_by': RequestsView.default_order_by,
            'options_show': RequestsView.show,
            'options_order_by': RequestsView().options_order_by,
            'options_order_dir': RequestsView().options_order_dir,
        }, context))
        self.assertQuerySetEqual(context['options_paths'], RequestsView()._get_paths())
        self.assertNotIn('path', context)
        self.assertIn('results', context)

    def test_get(self):
        show = 10
        path = '/path/to/somewhere/'
        order_by = 'path'
        response = self.client.get(silky_reverse('requests'), {
            'show': show,
            'path': path,
            'order_by': order_by,
        })
        context = response.context
        self.assertTrue(dict_contains({
            'show': show,
            'order_by': order_by,
            'path': path,
            'options_show': RequestsView.show,
            'options_order_by': RequestsView().options_order_by,
            'options_order_dir': RequestsView().options_order_dir,
        }, context))
        self.assertQuerySetEqual(context['options_paths'], RequestsView()._get_paths())
        self.assertIn('results', context)

    def test_post(self):
        response = self.client.post(silky_reverse('requests'), {
            'filter-overalltime-value': 100,
            'filter-overalltime-typ': 'TimeSpentOnQueriesFilter',
        })
        context = response.context
        self.assertTrue(dict_contains({
            'filters': {
                'overalltime': {'typ': 'TimeSpentOnQueriesFilter', 'value': 100, 'str': 'DB Time >= 100'}
            },
        }, context))
        self.assertQuerySetEqual(context['options_paths'], RequestsView()._get_paths())
        self.assertIn('results', context)

    def test_view_without_session_and_auth_middlewares(self):
        """
        Filters are not present because there is no `session` to store them.
        """
        with self.modify_settings(MIDDLEWARE={
            'remove': [
                'django.contrib.sessions.middleware.SessionMiddleware',
                'django.contrib.auth.middleware.AuthenticationMiddleware',
                'django.contrib.messages.middleware.MessageMiddleware',
            ],
        }):
            # test filters on GET
            show = 10
            path = '/path/to/somewhere/'
            order_by = 'path'
            response = self.client.get(silky_reverse('requests'), {
                'show': show,
                'path': path,
                'order_by': order_by,
            })
            context = response.context
            self.assertTrue(dict_contains({
                'show': show,
                'order_by': order_by,
                'path': path,
            }, context))

            # test filters on POST
            response = self.client.post(silky_reverse('requests'), {
                'filter-overalltime-value': 100,
                'filter-overalltime-typ': 'TimeSpentOnQueriesFilter',
            })
            context = response.context
            self.assertTrue(dict_contains({
                'filters': {
                    'overalltime': {'typ': 'TimeSpentOnQueriesFilter', 'value': 100, 'str': 'DB Time >= 100'}
                },
            }, context))


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
        super().setUpClass()
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


class TestNPlusOneViewFilter(TestCase):
    """Integration tests for the NPlusOneFilter wired through the requests view."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        now = django_timezone.now()

        # Request WITH N+1: 3 structurally identical queries
        cls.n1_request = models.Request.objects.create(
            method='GET', path='/n1-view/', num_sql_queries=3,
            start_time=now, end_time=now, time_taken=10,
        )
        models.Response.objects.create(
            request=cls.n1_request, status_code=200,
            encoded_headers='{}', body='',
        )
        for i in range(1, 4):
            models.SQLQuery.objects.create(
                query=f'SELECT * FROM "silk_request" WHERE "silk_request"."id" = {i}',
                start_time=now, end_time=now, traceback='',
                request=cls.n1_request,
            )

        # Request WITHOUT N+1: one structurally unique query
        cls.clean_request = models.Request.objects.create(
            method='GET', path='/clean-view/', num_sql_queries=1,
            start_time=now, end_time=now, time_taken=5,
        )
        models.Response.objects.create(
            request=cls.clean_request, status_code=200,
            encoded_headers='{}', body='',
        )
        models.SQLQuery.objects.create(
            query='SELECT COUNT(*) FROM "silk_request"',
            start_time=now, end_time=now, traceback='',
            request=cls.clean_request,
        )

    def test_n1_filter_shows_only_n1_requests(self):
        """POSTing NPlusOneFilter must include N+1 requests and exclude clean ones."""
        response = self.client.post(silky_reverse('requests'), {
            'filter-nplusone-typ': 'NPlusOneFilter',
            'filter-nplusone-value': '1',
        })
        self.assertEqual(response.status_code, 200)
        result_pks = [str(r.pk) for r in response.context['results']]
        self.assertIn(str(self.n1_request.pk), result_pks)
        self.assertNotIn(str(self.clean_request.pk), result_pks)

    def test_n1_filter_stored_in_context(self):
        """After POSTing NPlusOneFilter the context filters dict contains it."""
        response = self.client.post(silky_reverse('requests'), {
            'filter-nplusone-typ': 'NPlusOneFilter',
            'filter-nplusone-value': '1',
        })
        filters = response.context['filters']
        self.assertTrue(
            any(f.get('typ') == 'NPlusOneFilter' for f in filters.values()),
            'NPlusOneFilter not found in context filters',
        )

    def test_has_n1_annotation_on_page_results(self):
        """_create_context annotates page items with has_n1 based on SQL patterns."""
        response = self.client.get(silky_reverse('requests'))
        results = list(response.context['results'])
        result_pks = [str(r.pk) for r in results]

        if str(self.n1_request.pk) in result_pks:
            n1_result = next(r for r in results if str(r.pk) == str(self.n1_request.pk))
            self.assertTrue(n1_result.has_n1)

        if str(self.clean_request.pk) in result_pks:
            clean_result = next(r for r in results if str(r.pk) == str(self.clean_request.pk))
            self.assertFalse(clean_result.has_n1)

    def test_clear_filters_removes_n1_filter(self):
        """Submitting clear_filters after an N+1 filter resets to show all requests."""
        # First apply the filter
        self.client.post(silky_reverse('requests'), {
            'filter-nplusone-typ': 'NPlusOneFilter',
            'filter-nplusone-value': '1',
        })
        # Then clear it
        response = self.client.post(silky_reverse('requests'), {'clear_filters': '1'})
        self.assertEqual(response.status_code, 200)
        result_pks = [str(r.pk) for r in response.context['results']]
        self.assertIn(str(self.clean_request.pk), result_pks)
