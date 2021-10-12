from django.test import TestCase

from silk.collector import DataCollector


class TestCollector(TestCase):
    def test_singleton(self):
        a = DataCollector()
        b = DataCollector()
        c = DataCollector()
        self.assertTrue(a == b == c)

    def test_query_registration(self):
        mock_query = {}
        DataCollector().register_query(mock_query)
        self.assertIn(mock_query, list(DataCollector().queries.values()))

    def test_clear(self):
        self.test_query_registration()
        DataCollector().clear()
        self.assertFalse(DataCollector().queries)
