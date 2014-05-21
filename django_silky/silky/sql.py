import traceback
from django.db.models.sql import EmptyResultSet
from django.utils import timezone
from silky import models
from silky.local import DataCollector


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
        query_model = models.SQLQuery(query=q % params,
                                      traceback=tb)
        try:
            return self._execute_sql(*args, **kwargs)
        finally:
            query_model.end_time = timezone.now()
            DataCollector().register_query(query_model)
    else:
        return self._execute_sql(*args, **kwargs)