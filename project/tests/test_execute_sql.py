from unittest.mock import Mock, NonCallableMagicMock, NonCallableMock, patch

from django.test import TestCase

from silk.collector import DataCollector
from silk.models import Request, SQLQuery
from silk.sql import execute_sql

from .util import delete_all_models

_simple_mock_query_sql = 'SELECT * FROM table_name'
_simple_mock_query_params = ()


def mock_sql(mock_query_sql, mock_query_params):
    mock_sql_query = Mock(spec_set=['_execute_sql', 'query', 'as_sql', 'connection'])
    mock_sql_query._execute_sql = Mock()
    mock_sql_query.query = NonCallableMock(spec_set=['model'])
    mock_sql_query.query.model = Mock()
    mock_sql_query.as_sql = Mock(return_value=(mock_query_sql, mock_query_params))

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
        ops=NonCallableMock(spec_set=['explain_query_prefix']),
    )

    return mock_sql_query, _simple_mock_query_sql


def call_execute_sql(cls, request):
    DataCollector().configure(request=request)
    delete_all_models(SQLQuery)
    cls.mock_sql, cls.query_string = mock_sql(_simple_mock_query_sql, _simple_mock_query_params)
    kwargs = {
        'one': 1,
        'two': 2
    }
    cls.args = [1, 2]
    cls.kwargs = kwargs
    execute_sql(cls.mock_sql, *cls.args, **cls.kwargs)


class TestCallNoRequest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        call_execute_sql(cls, None)

    def tearDown(self):
        DataCollector().stop_python_profiler()

    def test_called(self):
        self.mock_sql._execute_sql.assert_called_once_with(*self.args, **self.kwargs)

    def test_count(self):
        self.assertEqual(0, len(DataCollector().queries))


class TestCallRequest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        call_execute_sql(cls, Request())

    def tearDown(self):
        DataCollector().stop_python_profiler()

    def test_called(self):
        self.mock_sql._execute_sql.assert_called_once_with(*self.args, **self.kwargs)

    def test_count(self):
        self.assertEqual(1, len(DataCollector().queries))

    def test_query(self):
        query = list(DataCollector().queries.values())[0]
        self.assertEqual(query['query'], self.query_string)


class TestCallSilky(TestCase):
    def tearDown(self):
        DataCollector().stop_python_profiler()

    def test_no_effect(self):
        DataCollector().configure()
        sql, _ = mock_sql(_simple_mock_query_sql, _simple_mock_query_params)
        sql.query.model = NonCallableMagicMock(spec_set=['__module__'])
        sql.query.model.__module__ = 'silk.models'
        # No SQLQuery models should be created for silk requests for obvious reasons
        with patch('silk.sql.DataCollector', return_value=Mock()) as mock_DataCollector:
            execute_sql(sql)
            self.assertFalse(mock_DataCollector().register_query.call_count)


class TestCollectorInteraction(TestCase):
    def tearDown(self):
        DataCollector().stop_python_profiler()

    def _query(self):
        try:
            query = list(DataCollector().queries.values())[0]
        except IndexError:
            self.fail('No queries created')
        return query

    def test_request(self):
        DataCollector().configure(request=Request.objects.create(path='/path/to/somewhere'))
        sql, _ = mock_sql(_simple_mock_query_sql, _simple_mock_query_params)
        execute_sql(sql)
        query = self._query()
        self.assertEqual(query['request'], DataCollector().request)

    def test_registration(self):
        DataCollector().configure(request=Request.objects.create(path='/path/to/somewhere'))
        sql, _ = mock_sql(_simple_mock_query_sql, _simple_mock_query_params)
        execute_sql(sql)
        query = self._query()
        self.assertIn(query, DataCollector().queries.values())

    def test_explain(self):
        DataCollector().configure(request=Request.objects.create(path='/path/to/somewhere'))
        sql, qs = mock_sql(_simple_mock_query_sql, _simple_mock_query_params)
        prefix = "EXPLAIN"
        mock_cursor = sql.connection.cursor.return_value.__enter__.return_value
        sql.connection.ops.explain_query_prefix.return_value = prefix
        execute_sql(sql)
        mock_cursor.execute.assert_called_once_with(f"{prefix} {qs}", ())
