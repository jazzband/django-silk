from time import sleep

from django.test import TestCase
from rawes.elastic_exception import ElasticException

from silk.esearch.model import ESIndexer
from silk.models import Request
from silk.tests import MockSuite


mock_suite = MockSuite()

TTW = 0.5  # Time to wait for changes to ES to be effective


class TestESIndexer(ESIndexer):
    index = 'test_index'


def _clear_elasticsearch():
    """
    Clear the test index of any data.
    """
    es = TestESIndexer._get_http_connection()
    try:
        es.delete('/' + TestESIndexer.index)
    except ElasticException as e:
        if e.status_code != 404:
            raise
    sleep(TTW)


class TestSerialisation(TestCase):
    """
    Test serialisation of Django model -> Dictionary ready to be sent to Elasticsearch
    """

    @classmethod
    def setUpClass(cls):
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


class TestSaveRequest(TestCase):
    """
    Test saving of models to Elasticsearch
    """

    @classmethod
    def setUpClass(cls):
        _clear_elasticsearch()
        r = mock_suite.mock_request()
        cls.response = TestESIndexer(r).http_insert()

    def test_index(self):
        """
        Attaching an index to the model should override the default index
        """
        self.assertEqual(self.response['_index'], TestESIndexer.index)

    def test_type(self):
        """
        The elasticsearch type should match the model class.
        """
        self.assertEqual(self.response['_type'], Request.__name__)

    def test_id(self):
        """
        Ensure that was actually saved down with an identifier
        """
        self.assertIn('_id', self.response)


class TestSaveRequestBulk(TestCase):
    """
    Test saving a list of models to Elasticsearch
    """

    @classmethod
    def setUpClass(cls):
        _clear_elasticsearch()
        requests = [mock_suite.mock_request() for _ in range(0, 10)]
        cls.response = TestESIndexer(requests).http_insert()

    def test_index(self):
        """
        Attaching an index to the model should override the default index
        """
        for d in self.response['items']:
            v = d.values()[0]
            self.assertEqual(v['_index'], TestESIndexer.index)

    def test_no_errors(self):
        self.assertFalse(self.response['errors'])

    def test_type(self):
        """
        The elasticsearch type should match the model class.
        """
        for d in self.response['items']:
            v = d.values()[0]
            self.assertEqual(v['_type'], Request.__name__)

