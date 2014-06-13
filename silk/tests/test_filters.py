import calendar
from datetime import timedelta
import random

from django.utils import timezone
from django.test import TestCase

from silk import models
from silk.request_filters import SecondsFilter, AfterDateFilter, BeforeDateFilter, ViewNameFilter, PathFilter
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

    def test_after_date_filter(self):
        requests = [mock_suite.mock_request() for _ in range(0, 10)]
        r = random.choice(requests)
        dt = r.start_time
        requuests = models.Request.objects.filter(AfterDateFilter(dt))
        for r in requuests:
            self.assertTrue(r.start_time > dt)

    def test_before_date_filter(self):
        requests = [mock_suite.mock_request() for _ in range(0, 10)]
        r = random.choice(requests)
        dt = r.start_time
        requuests = models.Request.objects.filter(BeforeDateFilter(dt))
        for r in requuests:
            self.assertTrue(r.start_time < dt)

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

