import logging
import traceback

from django.core.exceptions import EmptyResultSet
from django.utils import timezone
from django.utils.encoding import force_str

from silk.collector import DataCollector
from silk.config import SilkyConfig

Logger = logging.getLogger('silk.sql')


def _should_wrap(sql_query):
    if not DataCollector().request:
        return False

    for ignore_str in SilkyConfig().SILKY_IGNORE_QUERIES:
        if ignore_str in sql_query:
            return False
    return True


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
                prefix = connection.ops.explain_query_prefix(
                    analyze=True, **(SilkyConfig().SILKY_EXPLAIN_FLAGS or {})
                )
            except ValueError as error:
                error_str = str(error)
                if error_str.startswith("Unknown options:"):
                    Logger.warning(
                        "Database does not support analyzing queries with provided params. %s."
                        "SILKY_ANALYZE_QUERIES option will be ignored",
                        error_str
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


def execute_sql(self, *args, **kwargs):
    """wrapper around real execute_sql in order to extract information"""

    try:
        q, params = self.as_sql()
        if not q:
            raise EmptyResultSet
    except EmptyResultSet:
        try:
            result_type = args[0]
        except IndexError:
            result_type = kwargs.get('result_type', 'multi')
        if result_type == 'multi':
            return iter([])
        else:
            return
    sql_query = q % tuple(force_str(param) for param in params)
    if _should_wrap(sql_query):
        tb = ''.join(reversed(traceback.format_stack()))
        query_dict = {
            'query': sql_query,
            'start_time': timezone.now(),
            'traceback': tb
        }
        try:
            return self._execute_sql(*args, **kwargs)
        finally:
            query_dict['end_time'] = timezone.now()
            request = DataCollector().request
            if request:
                query_dict['request'] = request
            if getattr(self.query.model, '__module__', '') != 'silk.models':
                query_dict['analysis'] = _explain_query(self.connection, q, params)
                DataCollector().register_query(query_dict)
            else:
                DataCollector().register_silk_query(query_dict)
    return self._execute_sql(*args, **kwargs)
