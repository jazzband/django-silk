from django.test import TestCase

from silk.middleware import silky_reverse
from silk.views.summary import SummaryView

from .test_lib.assertion import dict_contains
from .test_lib.mock_suite import MockSuite

mock_suite = MockSuite()


class TestSummaryView(TestCase):
    def test_longest_query_by_view(self):
        [mock_suite.mock_request() for _ in range(0, 10)]
        print([x.time_taken for x in SummaryView()._longest_query_by_view([])])

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
            # test filters on POST
            seconds = 3600
            response = self.client.post(silky_reverse('summary'), {
                'filter-seconds-value': seconds,
                'filter-seconds-typ': 'SecondsFilter',
            })
            context = response.context
            self.assertTrue(dict_contains({
                'filters': {
                    'seconds': {'typ': 'SecondsFilter', 'value': seconds, 'str': f'>{seconds} seconds ago'}
                }
            }, context))
