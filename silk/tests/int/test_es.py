from time import sleep

from django.test import TestCase
from rawes.elastic_exception import ElasticException

from silk.esearch.model import ESIndexer
from silk.tests import MockSuite


mock_suite = MockSuite()

TTW = 0.5  # Time to wait for changes to ES to be effective


def _clear_elasticsearch():
    """
    Clear the test index of any data.
    """
    indexer = ESIndexer(None)
    es = indexer._get_http_connection()
    path = indexer._insert_path()
    try:
        es.delete(path)
    except ElasticException as e:
        if e.status_code != 404:
            raise
    sleep(TTW)


class TestESIndexer(ESIndexer):
    index = 'test_index'


class TestSerialisation(TestCase):
    """
    Test serialisation of Django model -> Dictionary ready to be sent to Elasticsearch
    """
    @classmethod
    def setUpClass(cls):
        _clear_elasticsearch()

    @classmethod
    def tearDownClass(cls):
        _clear_elasticsearch()

    def test_standard_fields(self):
        """
        fields declared directly on the model should be serialised
        """
        r = mock_suite.mock_request()
        indexer = TestESIndexer(r)
        serialisable = indexer.serialisable
        expected = ('time_taken', 'id', 'view_name', 'path', 'meta_time')
        for k in expected:
            self.assertIn(k, serialisable)

    def test_many_to_many(self):
        """
        many-to-many fields declared directly on the model should be serialised
        """
        p = mock_suite.mock_profile()
        indexer = TestESIndexer(p)
        serialisable = indexer.serialisable
        expected = ('queries',)
        for k in expected:
            self.assertIn(k, serialisable)

    def test_foreign_key(self):
        """
        ForeignKey declared directly on the model should be serialised
        """
        s = mock_suite.mock_sql_queries()[0]
        indexer = TestESIndexer(s)
        serialisable = indexer.serialisable
        expected = ('request',)
        for k in expected:
            self.assertIn(k, serialisable)

    def test_reverse_foreign_key(self):
        """
        fields declared implicity via related_name on a ForeignKey should be serialised
        """
        r = mock_suite.mock_request()
        indexer = TestESIndexer(r)
        serialisable = indexer.serialisable
        expected = ('queries',)
        for k in expected:
            self.assertIn(k, serialisable)

    def test_reverse_many_to_many(self):
        """
        fields declared implicitly via ManyToMany related_name should be serialised
        """
        r = mock_suite.mock_request()
        p = mock_suite.mock_profile(r)
        queries = mock_suite.mock_sql_queries(r, p)
        q = queries[0]
        indexer = TestESIndexer(q)
        serialisable = indexer.serialisable
        expected = ('profiles',)
        for k in expected:
            self.assertIn(k, serialisable)