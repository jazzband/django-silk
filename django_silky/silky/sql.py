import logging
import traceback

from django.conf import settings
from django.db.models.sql import EmptyResultSet
from django.utils import timezone
from pygments import highlight
from pygments.lexers.sql import SqlLexer
from pygments.formatters.terminal import TerminalFormatter

from silky import models
from silky.collector import DataCollector


Logger = logging.getLogger('silky')


def execute_sql(self, *args, **kwargs):
    """wrapper around real execute_sql in order to extract information"""
    if self.query.model.__module__ != 'silky.models':  # Otherwise infinite recursion when write to DB
        try:
            q, params = self.as_sql()
            if not q:
                raise EmptyResultSet
        except EmptyResultSet:
            if kwargs.get('result_type', 'multi') == 'multi':
                return iter([])
            else:
                return
        tb = ''.join(reversed(traceback.format_stack()))
        query = q % params
        query_model = models.SQLQuery(query=query,
                                      traceback=tb)
        try:
            return self._execute_sql(*args, **kwargs)
        finally:
            query_model.end_time = timezone.now()
            should_print = False
            try:
                should_print = settings.SILKY_PRINT
            except AttributeError:
                pass
            if should_print:
                formatter = TerminalFormatter()
                if Logger.isEnabledFor(logging.DEBUG):
                    Logger.debug('\n{sql} [{time_taken}ms]\n'.format(
                        sql=highlight(query_model.formatted_query, SqlLexer(), formatter).strip(),
                        time_taken=query_model.time_taken))
            request = DataCollector().request
            if request:
                query_model.request = request
            query_model.save()
            DataCollector().register_query(query_model)
    else:
        return self._execute_sql(*args, **kwargs)