import calendar
import random
from datetime import datetime, timedelta, timezone
from itertools import groupby
from math import floor

from django.test import TestCase
from django.utils import timezone as django_timezone

from silk import models
from silk.request_filters import (
    AfterDateFilter,
    BaseFilter,
    BeforeDateFilter,
    FilterValidationError,
    FunctionNameFilter,
    MethodFilter,
    MultiMethodFilter,
    MultiPathFilter,
    MultiStatusCodeFilter,
    NameFilter,
    NPlusOneFilter,
    NumQueriesFilter,
    OverallTimeFilter,
    PathFilter,
    SecondsFilter,
    StatusCodeFilter,
    TimeSpentOnQueriesFilter,
    ViewNameFilter,
)

from .test_lib.mock_suite import MockSuite
from .util import delete_all_models

mock_suite = MockSuite()


class TestRequestFilters(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def _time_stamp(self, dt):
        return calendar.timegm(dt.utctimetuple())

    def test_seconds_filter(self):
        requests = [mock_suite.mock_request() for _ in range(0, 10)]
        n = 0
        for r in requests:
            r.start_time = django_timezone.now() - timedelta(seconds=n)
            r.save()
            n += 1
        requests = models.Request.objects.filter(SecondsFilter(5))
        for r in requests:
            dt = r.start_time
            seconds = self._time_stamp(django_timezone.now()) - self._time_stamp(dt)
            self.assertTrue(seconds < 6)  # 6 to give a bit of leeway in case takes too long

    def test_view_name_filter(self):
        requests = [mock_suite.mock_request() for _ in range(0, 10)]
        r = random.choice(requests)
        view_name = r.view_name
        requests = models.Request.objects.filter(ViewNameFilter(view_name))
        for r in requests:
            self.assertTrue(r.view_name == view_name)

    def test_path_filter(self):
        requests = [mock_suite.mock_request() for _ in range(0, 10)]
        r = random.choice(requests)
        path = r.path
        requests = models.Request.objects.filter(PathFilter(path))
        for r in requests:
            self.assertTrue(r.path == path)

    def test_num_queries_filter(self):
        requests = [mock_suite.mock_request() for _ in range(0, 10)]
        counts = sorted(x.queries.count() for x in requests)
        c = counts[int(floor(len(counts) / 2))]
        num_queries_filter = NumQueriesFilter(c)
        query_set = models.Request.objects.all()
        query_set = num_queries_filter.contribute_to_query_set(query_set)
        filtered = query_set.filter(num_queries_filter)
        for f in filtered:
            self.assertGreaterEqual(f.queries.count(), c)

    def test_time_spent_queries_filter(self):
        requests = [mock_suite.mock_request() for _ in range(0, 10)]
        time_taken = sorted(sum(q.time_taken for q in x.queries.all()) for x in requests)
        c = time_taken[int(floor(len(time_taken) / 2))]
        time_taken_filter = TimeSpentOnQueriesFilter(c)
        query_set = models.Request.objects.all()
        query_set = time_taken_filter.contribute_to_query_set(query_set)
        filtered = query_set.filter(time_taken_filter)
        for f in filtered:
            self.assertGreaterEqual(sum(q.time_taken for q in f.queries.all()), c)

    def test_time_spent_filter(self):
        requests = [mock_suite.mock_request() for _ in range(0, 10)]
        time_taken = sorted(x.time_taken for x in requests)
        c = time_taken[int(floor(len(time_taken) / 2))]
        time_taken_filter = OverallTimeFilter(c)
        query_set = models.Request.objects.all()
        query_set = time_taken_filter.contribute_to_query_set(query_set)
        filtered = query_set.filter(time_taken_filter)
        for f in filtered:
            self.assertGreaterEqual(round(f.time_taken), round(c))

    def test_status_code_filter(self):
        requests = [mock_suite.mock_request() for _ in range(0, 50)]
        requests = sorted(requests, key=lambda x: x.response.status_code)
        by_status_code = groupby(requests, key=lambda x: x.response.status_code)
        for status_code, expected in by_status_code:
            status_code_filter = StatusCodeFilter(status_code)
            query_set = models.Request.objects.all()
            query_set = status_code_filter.contribute_to_query_set(query_set)
            filtered = query_set.filter(status_code_filter)
            self.assertEqual(len(list(expected)), filtered.count())

    def test_method_filter(self):
        requests = [mock_suite.mock_request() for _ in range(0, 50)]
        requests = sorted(requests, key=lambda x: x.method)
        by_method = groupby(requests, key=lambda x: x.method)
        for method, expected in by_method:
            method_filter = MethodFilter(method)
            query_set = models.Request.objects.all()
            query_set = method_filter.contribute_to_query_set(query_set)
            filtered = query_set.filter(method_filter)
            self.assertEqual(len(list(expected)), filtered.count())


class TestRequestAfterDateFilter(TestCase):
    def assertFilter(self, dt, f):
        requests = models.Request.objects.filter(f)
        for r in requests:
            self.assertTrue(r.start_time > dt)

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.requests = [mock_suite.mock_request() for _ in range(0, 10)]

    def test_after_date_filter(self):
        r = random.choice(self.requests)
        dt = r.start_time
        f = AfterDateFilter(dt)
        self.assertFilter(dt, f)

    def test_after_date_filter_str(self):
        r = random.choice(self.requests)
        dt = r.start_time
        fmt = AfterDateFilter.fmt
        dt_str = dt.strftime(fmt)
        date_filter = AfterDateFilter
        f = date_filter(dt_str)
        new_dt = datetime.strptime(dt_str, fmt)
        new_dt = django_timezone.make_aware(new_dt, timezone.utc)
        self.assertFilter(new_dt, f)


class TestRequestBeforeDateFilter(TestCase):
    def assertFilter(self, dt, f):
        requests = models.Request.objects.filter(f)
        for r in requests:
            self.assertTrue(r.start_time < dt)

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.requests = [mock_suite.mock_request() for _ in range(0, 10)]

    def test_before_date_filter(self):
        r = random.choice(self.requests)
        dt = r.start_time
        f = BeforeDateFilter(dt)
        self.assertFilter(dt, f)

    def test_before_date_filter_str(self):
        r = random.choice(self.requests)
        dt = r.start_time
        fmt = BeforeDateFilter.fmt
        dt_str = dt.strftime(fmt)
        date_filter = BeforeDateFilter
        f = date_filter(dt_str)
        new_dt = datetime.strptime(dt_str, fmt)
        new_dt = django_timezone.make_aware(new_dt, timezone.utc)
        self.assertFilter(new_dt, f)


class TestProfileFilters(TestCase):
    def setUp(self):
        delete_all_models(models.Profile)

    def test_name_filter(self):
        profiles = mock_suite.mock_profiles(n=10)
        p = random.choice(profiles)
        name = p.name
        requests = models.Profile.objects.filter(NameFilter(name))
        for p in requests:
            self.assertTrue(p.name == name)

    def test_function_name_filter(self):
        profiles = mock_suite.mock_profiles(n=10)
        p = random.choice(profiles)
        func_name = p.func_name
        requests = models.Profile.objects.filter(FunctionNameFilter(func_name))
        for p in requests:
            self.assertTrue(p.func_name == func_name)

    def test_num_queries_filter(self):
        profiles = mock_suite.mock_profiles(n=10)
        counts = sorted(x.queries.count() for x in profiles)
        c = counts[int(floor(len(counts) / 2))]
        num_queries_filter = NumQueriesFilter(c)
        query_set = models.Profile.objects.all()
        query_set = num_queries_filter.contribute_to_query_set(query_set)
        filtered = query_set.filter(num_queries_filter)
        for f in filtered:
            self.assertGreaterEqual(f.queries.count(), c)

    def test_time_spent_queries_filter(self):
        profiles = mock_suite.mock_profiles(n=10)
        time_taken = sorted(sum(q.time_taken for q in x.queries.all()) for x in profiles)
        c = time_taken[int(floor(len(time_taken) / 2))]
        time_taken_filter = TimeSpentOnQueriesFilter(c)
        query_set = models.Profile.objects.all()
        query_set = time_taken_filter.contribute_to_query_set(query_set)
        filtered = query_set.filter(time_taken_filter)
        for f in filtered:
            self.assertGreaterEqual(sum(q.time_taken for q in f.queries.all()), c)

    def test_time_spent_filter(self):
        profiles = [mock_suite.mock_request() for _ in range(0, 10)]
        time_taken = sorted(x.time_taken for x in profiles)
        c = time_taken[int(floor(len(time_taken) / 2))]
        time_taken_filter = OverallTimeFilter(c)
        query_set = models.Profile.objects.all()
        query_set = time_taken_filter.contribute_to_query_set(query_set)
        filtered = query_set.filter(time_taken_filter)
        for f in filtered:
            self.assertGreaterEqual(f.time_taken, c)


# ---------------------------------------------------------------------------
# Multi-select filter tests
# ---------------------------------------------------------------------------

class TestMultiMethodFilter(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        now = django_timezone.now()
        cls.get_request = models.Request.objects.create(
            method='GET', path='/mmf/', num_sql_queries=0,
            start_time=now, end_time=now, time_taken=10,
        )
        cls.post_request = models.Request.objects.create(
            method='POST', path='/mmf/', num_sql_queries=0,
            start_time=now, end_time=now, time_taken=10,
        )
        cls.put_request = models.Request.objects.create(
            method='PUT', path='/mmf/', num_sql_queries=0,
            start_time=now, end_time=now, time_taken=10,
        )

    def _base_qs(self):
        return models.Request.objects.filter(
            pk__in=[self.get_request.pk, self.post_request.pk, self.put_request.pk]
        )

    def _apply(self, f):
        return self._base_qs().filter(f)

    def test_single_method_json(self):
        qs = self._apply(MultiMethodFilter('["GET"]'))
        self.assertTrue(qs.filter(pk=self.get_request.pk).exists())
        self.assertFalse(qs.filter(pk=self.post_request.pk).exists())
        self.assertFalse(qs.filter(pk=self.put_request.pk).exists())

    def test_multiple_methods_json(self):
        qs = self._apply(MultiMethodFilter('["GET", "POST"]'))
        self.assertTrue(qs.filter(pk=self.get_request.pk).exists())
        self.assertTrue(qs.filter(pk=self.post_request.pk).exists())
        self.assertFalse(qs.filter(pk=self.put_request.pk).exists())

    def test_backward_compat_plain_string(self):
        """Old MethodFilter-style plain string is accepted."""
        qs = self._apply(MultiMethodFilter('GET'))
        self.assertTrue(qs.filter(pk=self.get_request.pk).exists())
        self.assertFalse(qs.filter(pk=self.post_request.pk).exists())

    def test_case_insensitive(self):
        qs = self._apply(MultiMethodFilter('["get"]'))
        self.assertTrue(qs.filter(pk=self.get_request.pk).exists())

    def test_empty_list_raises(self):
        with self.assertRaises(FilterValidationError):
            MultiMethodFilter('[]')

    def test_str_single(self):
        self.assertEqual(str(MultiMethodFilter('["GET"]')), 'Method == GET')

    def test_str_multiple(self):
        self.assertEqual(str(MultiMethodFilter('["GET", "POST"]')), 'Method in [GET, POST]')


class TestMultiPathFilter(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        now = django_timezone.now()
        cls.req_alpha = models.Request.objects.create(
            method='GET', path='/alpha/', num_sql_queries=0,
            start_time=now, end_time=now, time_taken=10,
        )
        cls.req_beta = models.Request.objects.create(
            method='GET', path='/beta/', num_sql_queries=0,
            start_time=now, end_time=now, time_taken=10,
        )
        cls.req_gamma = models.Request.objects.create(
            method='GET', path='/gamma/', num_sql_queries=0,
            start_time=now, end_time=now, time_taken=10,
        )

    def _base_qs(self):
        return models.Request.objects.filter(
            pk__in=[self.req_alpha.pk, self.req_beta.pk, self.req_gamma.pk]
        )

    def _apply(self, f):
        return self._base_qs().filter(f)

    def test_single_path_json(self):
        qs = self._apply(MultiPathFilter('["/alpha/"]'))
        self.assertTrue(qs.filter(pk=self.req_alpha.pk).exists())
        self.assertFalse(qs.filter(pk=self.req_beta.pk).exists())

    def test_multiple_paths_json(self):
        qs = self._apply(MultiPathFilter('["/alpha/", "/beta/"]'))
        self.assertTrue(qs.filter(pk=self.req_alpha.pk).exists())
        self.assertTrue(qs.filter(pk=self.req_beta.pk).exists())
        self.assertFalse(qs.filter(pk=self.req_gamma.pk).exists())

    def test_backward_compat_plain_string(self):
        """Old PathFilter-style plain string is accepted."""
        qs = self._apply(MultiPathFilter('/alpha/'))
        self.assertTrue(qs.filter(pk=self.req_alpha.pk).exists())
        self.assertFalse(qs.filter(pk=self.req_beta.pk).exists())

    def test_empty_list_raises(self):
        with self.assertRaises(FilterValidationError):
            MultiPathFilter('[]')

    def test_str_single(self):
        self.assertEqual(str(MultiPathFilter('["/alpha/"]')), 'Path == /alpha/')

    def test_str_multiple(self):
        self.assertEqual(str(MultiPathFilter('["/alpha/", "/beta/"]')), 'Path in [/alpha/, /beta/]')


class TestMultiStatusCodeFilter(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        now = django_timezone.now()
        for code in [200, 404, 500]:
            req = models.Request.objects.create(
                method='GET', path=f'/sc{code}/', num_sql_queries=0,
                start_time=now, end_time=now, time_taken=10,
            )
            models.Response.objects.create(
                request=req, status_code=code,
                encoded_headers='{}', body='',
            )
            setattr(cls, f'req_{code}', req)

    def _base_qs(self):
        return models.Request.objects.filter(
            pk__in=[self.req_200.pk, self.req_404.pk, self.req_500.pk]
        )

    def _apply(self, f):
        return self._base_qs().filter(f)

    def test_single_code_json(self):
        qs = self._apply(MultiStatusCodeFilter('[200]'))
        self.assertTrue(qs.filter(pk=self.req_200.pk).exists())
        self.assertFalse(qs.filter(pk=self.req_404.pk).exists())

    def test_multiple_codes_json(self):
        qs = self._apply(MultiStatusCodeFilter('[200, 404]'))
        self.assertTrue(qs.filter(pk=self.req_200.pk).exists())
        self.assertTrue(qs.filter(pk=self.req_404.pk).exists())
        self.assertFalse(qs.filter(pk=self.req_500.pk).exists())

    def test_backward_compat_plain_int_string(self):
        """Old StatusCodeFilter-style '200' string is accepted."""
        qs = self._apply(MultiStatusCodeFilter('200'))
        self.assertTrue(qs.filter(pk=self.req_200.pk).exists())
        self.assertFalse(qs.filter(pk=self.req_404.pk).exists())

    def test_empty_list_raises(self):
        with self.assertRaises(FilterValidationError):
            MultiStatusCodeFilter('[]')

    def test_str_single(self):
        self.assertEqual(str(MultiStatusCodeFilter('[200]')), 'Status == 200')

    def test_str_multiple(self):
        self.assertEqual(str(MultiStatusCodeFilter('[200, 404]')), 'Status in [200, 404]')


# ---------------------------------------------------------------------------
# NPlusOneFilter tests
# ---------------------------------------------------------------------------

class TestNPlusOneFilter(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        now = django_timezone.now()

        # Request WITH N+1: 3 structurally identical queries (same fingerprint)
        cls.n1_request = models.Request.objects.create(
            method='GET', path='/n1/', num_sql_queries=3,
            start_time=now, end_time=now, time_taken=10,
        )
        for i in range(1, 4):
            models.SQLQuery.objects.create(
                query=f'SELECT * FROM "auth_user" WHERE "auth_user"."id" = {i}',
                start_time=now, end_time=now, traceback='',
                request=cls.n1_request,
            )

        # Request WITHOUT N+1: structurally distinct queries
        cls.clean_request = models.Request.objects.create(
            method='GET', path='/clean/', num_sql_queries=2,
            start_time=now, end_time=now, time_taken=5,
        )
        for sql in [
            'SELECT "silk_request"."id" FROM "silk_request"',
            'SELECT COUNT(*) FROM "auth_permission"',
        ]:
            models.SQLQuery.objects.create(
                query=sql, start_time=now, end_time=now, traceback='',
                request=cls.clean_request,
            )

    def _apply_n1(self, qs):
        return NPlusOneFilter('1').contribute_to_query_set(qs)

    def _scoped_qs(self):
        return models.Request.objects.filter(
            pk__in=[self.n1_request.pk, self.clean_request.pk]
        )

    def test_n1_request_is_included(self):
        qs = self._apply_n1(self._scoped_qs())
        self.assertTrue(qs.filter(pk=self.n1_request.pk).exists())

    def test_clean_request_is_excluded(self):
        qs = self._apply_n1(self._scoped_qs())
        self.assertFalse(qs.filter(pk=self.clean_request.pk).exists())

    def test_below_threshold_not_flagged(self):
        """2 identical queries (below threshold of 3) must not be flagged."""
        now = django_timezone.now()
        req = models.Request.objects.create(
            method='GET', path='/two-same/', num_sql_queries=2,
            start_time=now, end_time=now, time_taken=5,
        )
        for _ in range(2):
            models.SQLQuery.objects.create(
                query='SELECT * FROM "silk_request" WHERE id = 1',
                start_time=now, end_time=now, traceback='',
                request=req,
            )
        qs = self._apply_n1(models.Request.objects.filter(pk=req.pk))
        self.assertFalse(qs.filter(pk=req.pk).exists())

    def test_empty_queryset_returns_empty(self):
        f = NPlusOneFilter('1')
        qs = f.contribute_to_query_set(models.Request.objects.none())
        self.assertEqual(qs.count(), 0)

    def test_str(self):
        self.assertEqual(str(NPlusOneFilter('1')), 'Has N+1 queries')

    def test_serialization_round_trip(self):
        f = NPlusOneFilter('1')
        d = f.as_dict()
        self.assertEqual(d['typ'], 'NPlusOneFilter')
        self.assertEqual(d['value'], '1')
        restored = BaseFilter.from_dict(d)
        self.assertIsInstance(restored, NPlusOneFilter)
        self.assertEqual(str(restored), 'Has N+1 queries')
