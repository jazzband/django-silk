from django.test import TestCase
from silk.collector import DataCollector
from silk.models import SQLQuery


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

    def test_finalise(self):
        """
        Just call the example app to try a full registration/finalise run
        """
        self.client.get("/example_app/")
        assert SQLQuery.objects.count() == 1
        query = SQLQuery.objects.get()
        assert (
            query.details.query
            == 'SELECT "example_app_blind"."id", "example_app_blind"."photo", "example_app_blind"."name", "example_app_blind"."child_safe" FROM "example_app_blind"'
        )
        assert query.details.traceback != ""
        assert query.details.analysis == "2 0 0 SCAN example_app_blind"
