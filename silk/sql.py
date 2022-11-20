import logging
import traceback

from django.apps import apps
from django.db import connection
from django.utils import timezone
from django.utils.encoding import force_str

from silk.config import SilkyConfig

Logger = logging.getLogger('silk.sql')


def _unpack_explanation(result):
    for row in result:
        if not isinstance(row, str):
            yield ' '.join(str(c) for c in row)
        else:
            yield row


def _explain_query(connection, q, params):
    if connection.features.supports_explaining_query_execution:
        if SilkyConfig().SILKY_ANALYZE_QUERIES:
            # Work around some DB engines not supporting analyze option
            try:
                prefix = connection.ops.explain_query_prefix(analyze=True, **(SilkyConfig().SILKY_EXPLAIN_FLAGS or {}))
            except ValueError as error:
                error_str = str(error)
                if error_str.startswith("Unknown options:"):
                    Logger.warning(
                        "Database does not support analyzing queries with provided params. %s. "
                        "SILKY_ANALYZE_QUERIES option will be ignored",
                        error_str,
                    )
                    prefix = connection.ops.explain_query_prefix()
                else:
                    raise error
        else:
            prefix = connection.ops.explain_query_prefix()

        # currently we cannot use explain() method
        # for queries other than `select`
        prefixed_query = f"{prefix} {q}"
        with connection.cursor() as cur:
            cur.execute(prefixed_query, params)
            result = _unpack_explanation(cur.fetchall())
            return '\n'.join(result)
    return None


class SilkQueryWrapper:
    def __init__(self):
        # Local import to prevent messing app.ready()
        from silk.collector import DataCollector

        self.data_collector = DataCollector()
        self.silk_model_table_names = [model._meta.db_table for model in apps.get_app_config('silk').get_models()]

    def __call__(self, execute, sql, params, many, context):
        sql_query = sql % tuple(force_str(param) for param in params) if params else sql
        query_dict = None
        if self._should_wrap(sql_query):
            tb = ''.join(reversed(traceback.format_stack()))
            query_dict = {'query': sql_query, 'start_time': timezone.now(), 'traceback': tb}
        try:
            return execute(sql, params, many, context)
        finally:
            if query_dict:
                query_dict['end_time'] = timezone.now()
                request = self.data_collector.request
                if request:
                    query_dict['request'] = request
                if not any(table_name in sql_query for table_name in self.silk_model_table_names):
                    query_dict['analysis'] = _explain_query(connection, sql, params)
                    self.data_collector.register_query(query_dict)
                else:
                    self.data_collector.register_silk_query(query_dict)

    def _should_wrap(self, sql_query):
        # Must have a request ongoing
        if not self.data_collector.request:
            return False

        # Must not try to explain 'EXPLAIN' queries or transaction stuff
        if any(
            sql_query.startswith(keyword)
            for keyword in [
                'SAVEPOINT',
                'RELEASE SAVEPOINT',
                'ROLLBACK TO SAVEPOINT',
                'PRAGMA',
                connection.ops.explain_query_prefix(),
            ]
        ):
            return False

        for ignore_str in SilkyConfig().SILKY_IGNORE_QUERIES:
            if ignore_str in sql_query:
                return False
        return True
