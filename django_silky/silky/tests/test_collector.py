import unittest
from mock import Mock
from silky.collector import DataCollector


class TestCollector(unittest.TestCase):
    def test_singleton(self):
        a = DataCollector()
        b = DataCollector()
        c = DataCollector()
        self.assertTrue(a == b == c)

    def test_query_registration(self):
        mock_query = Mock(spec_set=[])
        DataCollector().register_query(mock_query)
        self.assertIn(mock_query, DataCollector().queries)

    def test_clear(self):
        self.test_query_registration()
        DataCollector().clear()
        self.assertFalse(DataCollector().queries)