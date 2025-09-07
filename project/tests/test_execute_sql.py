from unittest.mock import Mock, NonCallableMagicMock, NonCallableMock, patch

from django.test import TestCase
from django.utils.encoding import force_str

from silk.collector import DataCollector
from silk.models import Request, SQLQuery
from silk.sql import execute_sql

from .util import delete_all_models

_simple_mock_query_sql = 'SELECT * FROM table_name WHERE column1 = %s'
_simple_mock_query_params = ('asdf',)
_non_unicode_binary_mock_query_params = (b'\x0a\x00\x00\xff',)
_unicode_binary_mock_query_params = ('🫠'.encode(),)


def mock_sql(mock_query_params):
    mock_sql_query = Mock(spec_set=['_execute_sql', 'query', 'as_sql', 'connection'])
    mock_sql_query._execute_sql = Mock()
    mock_sql_query.query = NonCallableMock(spec_set=['model'])
    mock_sql_query.query.model = Mock()
    mock_sql_query.as_sql = Mock(return_value=(_simple_mock_query_sql, mock_query_params))

    mock_sql_query.connection = NonCallableMock(
        spec_set=['cursor', 'features', 'ops'],
        cursor=Mock(
            spec_set=['__call__'],
            return_value=NonCallableMagicMock(spec_set=['__enter__', '__exit__', 'execute'])
        ),
        features=NonCallableMock(
            spec_set=['supports_explaining_query_execution'],
            supports_explaining_query_execution=True
        ),
        ops=NonCallableMock(spec_set=['explain_query_prefix'],
                            explain_query_prefix=Mock(return_value='')),
    )

    return mock_sql_query, mock_query_params


class BaseTestCase(TestCase):
    def tearDown(self):
        DataCollector().stop_python_profiler()

    def call_execute_sql(self, request, mock_query_params):
        DataCollector().configure(request=request)
        delete_all_models(SQLQuery)
        self.query_string = _simple_mock_query_sql
        self.mock_sql, self.query_params = mock_sql(mock_query_params)
        self.kwargs = {
            'one': 1,
            'two': 2
        }
        self.args = [1, 2]
        execute_sql(self.mock_sql, *self.args, **self.kwargs)


class TestCallNoRequest(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.call_execute_sql(None, _simple_mock_query_params)

    def test_called(self):
        self.mock_sql._execute_sql.assert_called_once_with(*self.args, **self.kwargs)

    def test_count(self):
        self.assertEqual(0, len(DataCollector().queries))


class TestCallRequest(BaseTestCase):
    def test_query_simple(self):
        self.call_execute_sql(Request(), _simple_mock_query_params)
        self.mock_sql._execute_sql.assert_called_once_with(*self.args, **self.kwargs)
        self.assertEqual(1, len(DataCollector().queries))
        query = list(DataCollector().queries.values())[0]
        expected = self.query_string % tuple(force_str(param) for param in self.query_params)
        self.assertEqual(query['query'], expected)

    def test_query_unicode(self):
        self.call_execute_sql(Request(), _unicode_binary_mock_query_params)
        self.mock_sql._execute_sql.assert_called_once_with(*self.args, **self.kwargs)
        self.assertEqual(1, len(DataCollector().queries))
        query = list(DataCollector().queries.values())[0]
        expected = self.query_string % tuple(force_str(param) for param in self.query_params)
        self.assertEqual(query['query'], expected)

    def test_query_non_unicode(self):
        self.call_execute_sql(Request(), _non_unicode_binary_mock_query_params)
        self.mock_sql._execute_sql.assert_called_once_with(*self.args, **self.kwargs)
        self.assertEqual(0, len(DataCollector().queries))


class TestCallSilky(BaseTestCase):
    def test_no_effect(self):
        DataCollector().configure()
        sql, _ = mock_sql(_simple_mock_query_params)
        sql.query.model = NonCallableMagicMock(spec_set=['__module__'])
        sql.query.model.__module__ = 'silk.models'
        # No SQLQuery models should be created for silk requests for obvious reasons
        with patch('silk.sql.DataCollector', return_value=Mock()) as mock_DataCollector:
            execute_sql(sql)
            self.assertFalse(mock_DataCollector().register_query.call_count)


class TestCollectorInteraction(BaseTestCase):
    def _query(self):
        try:
            query = list(DataCollector().queries.values())[0]
        except IndexError:
            self.fail('No queries created')
        return query

    def test_request(self):
        DataCollector().configure(request=Request.objects.create(path='/path/to/somewhere'))
        sql, _ = mock_sql(_simple_mock_query_params)
        execute_sql(sql)
        query = self._query()
        self.assertEqual(query['request'], DataCollector().request)

    def test_registration(self):
        DataCollector().configure(request=Request.objects.create(path='/path/to/somewhere'))
        sql, _ = mock_sql(_simple_mock_query_params)
        execute_sql(sql)
        query = self._query()
        self.assertIn(query, DataCollector().queries.values())

    def test_explain_simple(self):
        DataCollector().configure(request=Request.objects.create(path='/path/to/somewhere'))
        sql, params = mock_sql(_simple_mock_query_params)
        prefix = "EXPLAIN"
        mock_cursor = sql.connection.cursor.return_value.__enter__.return_value
        sql.connection.ops.explain_query_prefix.return_value = prefix
        execute_sql(sql)
        self.assertNotIn(prefix, params)
        params = tuple(force_str(param) for param in params)
        mock_cursor.execute.assert_called_once_with(f"{prefix} {_simple_mock_query_sql}", params)

    def test_explain_unicode(self):
        DataCollector().configure(request=Request.objects.create(path='/path/to/somewhere'))
        sql, params = mock_sql(_unicode_binary_mock_query_params)
        prefix = "EXPLAIN"
        mock_cursor = sql.connection.cursor.return_value.__enter__.return_value
        sql.connection.ops.explain_query_prefix.return_value = prefix
        execute_sql(sql)
        self.assertNotIn(prefix, params)
        params = tuple(force_str(param) for param in params)
        mock_cursor.execute.assert_called_once_with(f"{prefix} {_simple_mock_query_sql}", params)

    def test_explain_non_unicode(self):
        DataCollector().configure(request=Request.objects.create(path='/path/to/somewhere'))
        sql, params = mock_sql(_non_unicode_binary_mock_query_params)
        prefix = "EXPLAIN"
        mock_cursor = sql.connection.cursor.return_value.__enter__.return_value
        sql.connection.ops.explain_query_prefix.return_value = prefix
        execute_sql(sql)
        self.assertNotIn(prefix, params)
        self.assertFalse(mock_cursor.execute.called)
