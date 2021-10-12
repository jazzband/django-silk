from django.test import TestCase

from silk.views.summary import SummaryView

from .test_lib.mock_suite import MockSuite

mock_suite = MockSuite()

class TestSummaryView(TestCase):
    def test_longest_query_by_view(self):
        [mock_suite.mock_request() for _ in range(0, 10)]
        print([x.time_taken for x in SummaryView()._longest_query_by_view([])])
