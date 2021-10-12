import calendar
import random
from datetime import datetime, timedelta
from itertools import groupby
from math import floor

import pytz
from django.test import TestCase
from django.utils import timezone

from silk import models
from silk.request_filters import (
    AfterDateFilter,
    BeforeDateFilter,
    FunctionNameFilter,
    MethodFilter,
    NameFilter,
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
            r.start_time = timezone.now() - timedelta(seconds=n)
            r.save()
            n += 1
        requests = models.Request.objects.filter(SecondsFilter(5))
        for r in requests:
            dt = r.start_time
            seconds = self._time_stamp(timezone.now()) - self._time_stamp(dt)
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
        new_dt = timezone.make_aware(new_dt, pytz.UTC)
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
        new_dt = timezone.make_aware(new_dt, pytz.UTC)
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
