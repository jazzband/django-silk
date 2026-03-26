"""
Django queryset filters used by the requests view
"""
import json
import logging
from datetime import datetime, timedelta

TIME_RANGE_PRESETS = {
    '1h': 3600,
    '6h': 21600,
    '24h': 86400,
    '7d': 604800,
}

from django.db.models import Count, Q, Sum
from django.utils import timezone

from silk.profiling.dynamic import _get_module
from silk.templatetags.silk_filters import _silk_date_time
from silk.utils.n_plus_one import fingerprint_query

logger = logging.getLogger('silk.request_filters')


class FilterValidationError(Exception):
    pass


class BaseFilter(Q):
    def __init__(self, value=None, *args, **kwargs):
        self.value = value
        super().__init__(*args, **kwargs)

    @property
    def typ(self):
        return self.__class__.__name__

    @property
    def serialisable_value(self):
        return self.value

    def as_dict(self):
        return {'typ': self.typ, 'value': self.serialisable_value, 'str': str(self)}

    @staticmethod
    def from_dict(d):
        typ = d['typ']
        filter_class = globals()[typ]
        val = d.get('value', None)
        return filter_class(val)

    def contribute_to_query_set(self, query_set):
        """
        make any changes to the query-set before the query is applied,
        e.g. annotate with extra fields
        :param query_set: a django queryset
        :return: a new query set that this filter can then be used with
        """
        return query_set


class SecondsFilter(BaseFilter):
    def __init__(self, n):
        if n:
            try:
                value = int(n)
            except ValueError as e:
                raise FilterValidationError(e)
            now = timezone.now()
            frm_dt = now - timedelta(seconds=value)
            super().__init__(value, start_time__gt=frm_dt)
        else:
            # Empty query
            super().__init__()

    def __str__(self):
        return '>%d seconds ago' % self.value


def _parse(dt, fmt):
    """attempt to coerce dt into a datetime given fmt, otherwise raise
    a FilterValidationError"""
    try:
        dt = datetime.strptime(dt, fmt)
    except TypeError:
        if not isinstance(dt, datetime):
            raise FilterValidationError('Must be a datetime object')
    except ValueError as e:
        raise FilterValidationError(e)
    return dt


class BeforeDateFilter(BaseFilter):
    fmt = '%Y/%m/%d %H:%M'

    def __init__(self, dt):
        value = _parse(dt, self.fmt)
        super().__init__(value, start_time__lt=value)

    @property
    def serialisable_value(self):
        return self.value.strftime(self.fmt)

    def __str__(self):
        return '<%s' % _silk_date_time(self.value)


class AfterDateFilter(BaseFilter):
    fmt = '%Y/%m/%d %H:%M'

    def __init__(self, dt):
        value = _parse(dt, self.fmt)
        super().__init__(value, start_time__gt=value)

    @property
    def serialisable_value(self):
        return self.value.strftime(self.fmt)

    def __str__(self):
        return '>%s' % _silk_date_time(self.value)


class ViewNameFilter(BaseFilter):
    """filter on the name of the view, e.g. the name=xyz component of include in urls.py"""

    def __init__(self, view_name):
        value = view_name
        super().__init__(value, view_name=view_name)

    def __str__(self):
        return 'View == %s' % self.value


class PathFilter(BaseFilter):
    """filter on path e.g. /path/to/something"""

    def __init__(self, path):
        value = path
        super().__init__(value, path=path)

    def __str__(self):
        return 'Path == %s' % self.value


class NameFilter(BaseFilter):
    def __init__(self, name):
        value = name
        super().__init__(value, name=name)

    def __str__(self):
        return 'name == %s' % self.value


class FunctionNameFilter(BaseFilter):
    def __init__(self, func_name):
        value = func_name
        super().__init__(value, func_name=func_name)

    def __str__(self):
        return 'func_name == %s' % self.value


class NumQueriesFilter(BaseFilter):
    def __init__(self, n):
        try:
            value = int(n)
        except ValueError as e:
            raise FilterValidationError(e)
        super().__init__(value, num_queries__gte=n)

    def __str__(self):
        return '#queries >= %s' % self.value

    def contribute_to_query_set(self, query_set):
        return query_set.annotate(num_queries=Count('queries'))


class TimeSpentOnQueriesFilter(BaseFilter):
    def __init__(self, n):
        try:
            value = int(n)
        except ValueError as e:
            raise FilterValidationError(e)
        super().__init__(value, db_time__gte=n)

    def __str__(self):
        return 'DB Time >= %s' % self.value

    def contribute_to_query_set(self, query_set):
        return query_set.annotate(db_time=Sum('queries__time_taken'))


class OverallTimeFilter(BaseFilter):
    def __init__(self, n):
        try:
            value = int(n)
        except ValueError as e:
            raise FilterValidationError(e)
        super().__init__(value, time_taken__gte=n)

    def __str__(self):
        return 'Time >= %s' % self.value


class StatusCodeFilter(BaseFilter):
    def __init__(self, n):
        try:
            value = int(n)
        except ValueError as e:
            raise FilterValidationError(e)
        super().__init__(value, response__status_code=n)


class MethodFilter(BaseFilter):
    def __init__(self, value):
        super().__init__(value, method=value)


class MultiMethodFilter(BaseFilter):
    """Filter on one or more HTTP methods. value is a JSON list e.g. '["GET", "POST"]'.
    Also accepts a plain string for backward compatibility with old MethodFilter sessions."""

    def __init__(self, value):
        if isinstance(value, str):
            try:
                parsed = json.loads(value)
                if isinstance(parsed, list):
                    methods = [str(m).upper() for m in parsed if m]
                else:
                    methods = [str(parsed).upper()] if parsed else []
            except (ValueError, TypeError):
                methods = [value.strip().upper()] if value.strip() else []
        else:
            methods = [str(m).upper() for m in value if m]

        if not methods:
            raise FilterValidationError('No methods selected')

        super().__init__(json.dumps(methods), method__in=methods)

    def __str__(self):
        try:
            methods = json.loads(self.value)
            if len(methods) == 1:
                return 'Method == %s' % methods[0]
            return 'Method in [%s]' % ', '.join(methods)
        except Exception:
            return 'Method: %s' % self.value


class MultiPathFilter(BaseFilter):
    """Filter on one or more paths. value is a JSON list e.g. '["/api/users/", "/api/products/"]'.
    Also accepts a plain string for backward compatibility with old PathFilter sessions."""

    def __init__(self, value):
        if isinstance(value, str):
            try:
                parsed = json.loads(value)
                if isinstance(parsed, list):
                    paths = [str(p) for p in parsed if p]
                else:
                    paths = [str(parsed)] if parsed else []
            except (ValueError, TypeError):
                paths = [value.strip()] if value.strip() else []
        else:
            paths = [str(p) for p in value if p]

        if not paths:
            raise FilterValidationError('No paths selected')

        super().__init__(json.dumps(paths), path__in=paths)

    def __str__(self):
        try:
            paths = json.loads(self.value)
            if len(paths) == 1:
                return 'Path == %s' % paths[0]
            return 'Path in [%s]' % ', '.join(paths)
        except Exception:
            return 'Path: %s' % self.value


class MultiStatusCodeFilter(BaseFilter):
    """Filter on one or more status codes. value is a JSON list e.g. '[200, 404]'.
    Also accepts a plain int string for backward compatibility."""

    def __init__(self, value):
        if isinstance(value, str):
            try:
                parsed = json.loads(value)
                if isinstance(parsed, list):
                    codes = [int(c) for c in parsed if c != '' and c is not None]
                else:
                    codes = [int(parsed)] if parsed != '' else []
            except (ValueError, TypeError):
                try:
                    codes = [int(value)]
                except (ValueError, TypeError):
                    codes = []
        else:
            codes = [int(c) for c in value if c]

        if not codes:
            raise FilterValidationError('No status codes selected')

        super().__init__(json.dumps(codes), response__status_code__in=codes)

    def __str__(self):
        try:
            codes = json.loads(self.value)
            if len(codes) == 1:
                return 'Status == %d' % codes[0]
            return 'Status in [%s]' % ', '.join(str(c) for c in codes)
        except Exception:
            return 'Status: %s' % self.value


class NPlusOneFilter(BaseFilter):
    """Filter requests that have potential N+1 SQL query patterns (3+ identical queries).

    All filtering is performed in contribute_to_query_set — the Q object itself is empty
    so the subsequent .filter(self) is a no-op. This mirrors the batch N+1 detection
    already used on the requests list page for badge display.
    """

    def __init__(self, value='1'):
        # value is a boolean flag ('1' = enabled).
        super().__init__(value)

    def contribute_to_query_set(self, query_set):
        from silk.models import SQLQuery  # local import avoids circular reference
        request_ids = list(query_set.values_list('pk', flat=True))
        if not request_ids:
            return query_set
        sql_rows = SQLQuery.objects.filter(
            request_id__in=request_ids
        ).values('request_id', 'query')
        buckets = {}
        for row in sql_rows:
            rid = row['request_id']
            fp = fingerprint_query(row['query'])
            buckets.setdefault(rid, {}).setdefault(fp, 0)
            buckets[rid][fp] += 1
        n1_ids = [
            rid for rid, fps in buckets.items()
            if any(cnt >= 3 for cnt in fps.values())
        ]
        return query_set.filter(pk__in=n1_ids)

    def __str__(self):
        return 'Has N+1 queries'


def filters_from_request(request):
    raw_filters = {}
    for key in request.POST:
        splt = key.split('-')
        if splt[0].startswith('filter'):
            ident = splt[1]
            typ = splt[2]
            if ident not in raw_filters:
                raw_filters[ident] = {}
            raw_filters[ident][typ] = request.POST[key]
    filters = {}
    for ident, raw_filter in raw_filters.items():
        value = raw_filter.get('value', '')
        if value.strip():
            typ = raw_filter['typ']
            module = _get_module('silk.request_filters')
            filter_class = getattr(module, typ)
            try:
                f = filter_class(value)
                filters[ident] = f
            except FilterValidationError:
                logger.warning(f'Validation error when processing filter {typ}({value})')
    return filters


def filters_from_data(data):
    """Same logic as filters_from_request but accepts a plain dict (e.g. request.POST or
    request.session data) instead of a Django request object."""
    raw_filters = {}
    for key in data:
        splt = key.split('-')
        if splt[0].startswith('filter'):
            ident = splt[1]
            typ = splt[2]
            if ident not in raw_filters:
                raw_filters[ident] = {}
            raw_filters[ident][typ] = data[key]
    filters = {}
    for ident, raw_filter in raw_filters.items():
        value = raw_filter.get('value', '')
        if value.strip():
            typ = raw_filter['typ']
            module = _get_module('silk.request_filters')
            filter_class = getattr(module, typ)
            try:
                f = filter_class(value)
                filters[ident] = f
            except FilterValidationError:
                logger.warning(f'Validation error when processing filter {typ}({value})')
    return filters


class FiltersManager:
    def __init__(self, filters_key):
        self.key = filters_key

    def save(self, request, filters):
        if hasattr(request, 'session'):
            request.session[self.key] = filters
        request.silk_filters = filters

    def get(self, request):
        if hasattr(request, 'session'):
            return request.session.get(self.key, {})
        return request.silk_filters
