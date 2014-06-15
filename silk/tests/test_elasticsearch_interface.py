from django.test import TestCase
from silk.esearch.model import ESIndexer, RequestIndexer
from silk.tests import MockSuite

mock_suite = MockSuite()


class TestSerialiser(TestCase):
    def test_requests(self):
        r = mock_suite.mock_request()
        indexer = RequestIndexer(r)
        s = indexer.serialisable
        self.assertTrue(s)
        self.assertIn('queries', s)
        queries = s['queries']
        for q in queries:
            self.assertIn('request', q)

    def test_profiles(self):
        r = mock_suite.mock_request()
        p = mock_suite.mock_profile(r)
        indexer = ESIndexer(p)
        s = indexer.serialisable
        self.assertIn('queries', s)
        self.assertIn('request', s)
        queries = s['queries']
        for q in queries:
            self.assertIn('request', q)