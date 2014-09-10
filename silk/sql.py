import logging
import traceback

from django.utils import timezone
from django.db import connection
from django.db.backends.util import CursorWrapper

from silk.collector import DataCollector
from silk.config import SilkyConfig

Logger = logging.getLogger('silk')


def _should_wrap(sql_query):
    for ignore_str in SilkyConfig().SILKY_IGNORE_QUERIES:
        if ignore_str in sql_query:
            return False
    return True


def wrap_cursor_execute():
    if getattr(connection.cursor, '__silk__wrapped', False):
        return
    original_get_cursor = connection.cursor

    def wrapped_get_cursor():
        cursor = original_get_cursor()
        return SilkyCursorWrapper(cursor, connection)

    wrapped_get_cursor.__silk__wrapped = True
    connection.cursor = wrapped_get_cursor


class SilkyCursorWrapper(CursorWrapper):
    def _should_wrap(self, sql, params):
        """
        :param sql:
        :param params:
        :return: String representation of sql query if should wrap, else false
        """
        sql_query = sql % params
        if _should_wrap(sql_query):
            return sql_query
        return False

    def execute(self, sql, params=()):
        sql_query = sql % params
        if not _should_wrap(sql_query):
            return self.cursor.execute(sql, params)
        tb = ''.join(reversed(traceback.format_stack()))
        query_dict = {
            'query': sql_query,
            'start_time': timezone.now(),
            'traceback': tb
        }
        try:
            return self.cursor.execute(sql, params)
        finally:
            query_dict['end_time'] = timezone.now()
            DataCollector().register_query(query_dict)

    def executemany(self, sql, param_list):
        sql_queries = [self._should_wrap(sql, params) for params in param_list]
        if not all(sql_queries):
            return self.cursor.executemany(sql, param_list)
        tb = ''.join(reversed(traceback.format_stack()))
        start_time = timezone.now()
        try:
            return self.cursor.executemany(sql, param_list)
        finally:
            for sql_query in sql_queries:
                # TODO: We can improve this by somehow finding the start/end time of each individual query.
                # TODO: Alternatively, we could add a ManySQLQuery model so we can at least acknowledge the fact.
                query_dict = {
                    'query': sql_query,
                    'start_time': start_time,
                    'end_time': timezone.now(),
                    'traceback': tb
                }
                DataCollector().register_query(query_dict)
