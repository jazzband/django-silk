import calendar
from datetime import timedelta, datetime
import random

from django.utils import timezone
from django.test import TestCase
import pytz

from silk import models
from silk.request_filters import SecondsFilter, AfterDateFilter, BeforeDateFilter, ViewNameFilter, PathFilter, NameFilter, FunctionNameFilter
from silk.tests import MockSuite


mock_suite = MockSuite()


class TestFilters(TestCase):
    @classmethod
    def setUpClass(cls):
        pass

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
            self.assertTrue(seconds < 5)

    def test_view_name_filter(self):
        requests = [mock_suite.mock_request() for _ in range(0, 10)]
        r = random.choice(requests)
        view_name = r.view_name
        requuests = models.Request.objects.filter(ViewNameFilter(view_name))
        for r in requuests:
            self.assertTrue(r.view_name == view_name)

    def test_path_filter(self):
        requests = [mock_suite.mock_request() for _ in range(0, 10)]
        r = random.choice(requests)
        path = r.path
        requuests = models.Request.objects.filter(PathFilter(path))
        for r in requuests:
            self.assertTrue(r.path == path)


class TestAfterDateFilter(TestCase):
    def assertFilter(self, dt, f):
        requuests = models.Request.objects.filter(f)
        for r in requuests:
            self.assertTrue(r.start_time > dt)

    @classmethod
    def setUpClass(cls):
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


class TestBeforeDateFilter(TestCase):
    def assertFilter(self, dt, f):
        requuests = models.Request.objects.filter(f)
        for r in requuests:
            self.assertTrue(r.start_time < dt)

    @classmethod
    def setUpClass(cls):
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

    def test_view_name_filter(self):
        profiles = mock_suite.mock_profiles(n=10)
        p = random.choice(profiles)
        name = p.name
        requuests = models.Profile.objects.filter(NameFilter(name))
        for p in requuests:
            self.assertTrue(p.name == name)

    def test_path_filter(self):
        profiles = mock_suite.mock_profiles(n=10)
        p = random.choice(profiles)
        path = p.func_name
        requuests = models.Profile.objects.filter(FunctionNameFilter(path))
        for p in requuests:
            self.assertTrue(p.func_name == path)