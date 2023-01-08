from django.test import TestCase

from silk.config import SilkyConfig
from silk.middleware import silky_reverse

from .test_lib.mock_suite import MockSuite


class TestViewSQL(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        SilkyConfig().SILKY_AUTHENTICATION = False
        SilkyConfig().SILKY_AUTHORISATION = False

    def test_duplicates_should_show(self):
        """Generate a lot of duplicates and test that they are visible on the page"""
        request = MockSuite().mock_request()
        request.queries.all().delete()
        # Ensure we have a amount of queries with the same structure
        query = MockSuite().mock_sql_queries(request=request, n=1)[0]
        for _ in range(0, 4):
            query.id = None
            query.save()
        url = silky_reverse('request_sql', kwargs={'request_id': request.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<td class="right-aligned">4</td>')
