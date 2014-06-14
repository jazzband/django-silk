"""Django queryset filters used by the requests view"""
from datetime import timedelta, datetime

from django.db.models import Q
from django.utils import timezone

from silk.templatetags.filters import _silk_date_time


class BaseFilter(Q):
    def __init__(self, value=None, *args, **kwargs):
        self.value = value
        super(BaseFilter, self).__init__(*args, **kwargs)

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


class SecondsFilter(BaseFilter):
    def __init__(self, n):
        if n:
            value = int(n)
            now = timezone.now()
            frm_dt = now - timedelta(seconds=value)
            super(SecondsFilter, self).__init__(value, start_time__gt=frm_dt)
        else:
            # Empty query
            super(SecondsFilter, self).__init__()

    def __str__(self):
        return 'Last %d seconds' % self.value




class BeforeDateFilter(BaseFilter):
    fmt = '%Y/%m/%d %H:%M'

    def __init__(self, dt):
        try:
            dt = datetime.strptime(dt, self.fmt)
        except TypeError:  # Assume its a datetime
            pass
        value = dt
        super(BeforeDateFilter, self).__init__(value, start_time__lt=dt)

    @property
    def serialisable_value(self):
        return self.value.strftime(self.fmt)

    def __str__(self):
        return '< %s' % _silk_date_time(self.value)


class AfterDateFilter(BaseFilter):
    fmt = '%Y/%m/%d %H:%M'

    def __init__(self, dt):
        try:
            dt = datetime.strptime(dt, self.fmt)
        except TypeError:  # Assume its a datetime
            pass
        value = dt
        super(AfterDateFilter, self).__init__(value, start_time__gt=dt)

    @property
    def serialisable_value(self):
        return self.value.strftime(self.fmt)


    def __str__(self):
        return '> %s' % _silk_date_time(self.value)


class ViewNameFilter(BaseFilter):
    """filter on the name of the view, e.g. the name=xyz component of include in urls.py"""

    def __init__(self, view_name):
        value = view_name
        super(ViewNameFilter, self).__init__(value, view_name=view_name)

    def __str__(self):
        return 'view == %s' % self.value


class PathFilter(BaseFilter):
    """filter on path e.g. /path/to/something"""

    def __init__(self, path):
        value = path
        super(PathFilter, self).__init__(value, path=path)

    def __str__(self):
        return 'path == %s' % self.value