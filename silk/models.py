import base64
import json
import random
import re
from uuid import uuid4

import sqlparse
from django.conf import settings
from django.core.files.storage import storages
from django.core.files.storage.handler import InvalidStorageError
from django.db import models, transaction
from django.db.models import (
    Avg,
    BooleanField,
    CharField,
    Count,
    DateTimeField,
    FileField,
    FloatField,
    ForeignKey,
    IntegerField,
    ManyToManyField,
    OneToOneField,
    Sum,
    TextField,
)
from django.shortcuts import render
from django.utils import timezone
from django.utils.safestring import mark_safe

from silk.config import SilkyConfig
from silk.utils.profile_parser import parse_profile

from .models import Request

try:
    silk_storage = storages['SILKY_STORAGE']
except InvalidStorageError:
    from django.utils.module_loading import import_string
    storage_class = SilkyConfig().SILKY_STORAGE_CLASS or settings.DEFAULT_FILE_STORAGE
    silk_storage = import_string(storage_class)()


# Seperated out so can use in tests w/o models
def _time_taken(start_time, end_time):
    d = end_time - start_time
    return d.seconds * 1000 + d.microseconds / 1000


def time_taken(self):
    return _time_taken(self.start_time, self.end_time)


class CaseInsensitiveDictionary(dict):
    def __getitem__(self, key):
        return super().__getitem__(key.lower())

    def __setitem__(self, key, value):
        super().__setitem__(key.lower(), value)

    def update(self, other=None, **kwargs):
        for k, v in other.items():
            self[k] = v
        for k, v in kwargs.items():
            self[k] = v

    def __init__(self, d):
        super().__init__()
        for k, v in d.items():
            self[k] = v


class Request(models.Model):
    id = CharField(max_length=36, default=uuid4, primary_key=True)
    path = CharField(max_length=190, db_index=True)
    query_params = TextField(blank=True, default='')
    raw_body = TextField(blank=True, default='')
    body = TextField(blank=True, default='')
    method = CharField(max_length=10)
    start_time = DateTimeField(default=timezone.now, db_index=True)
    view_name = CharField(
        max_length=190, db_index=True, blank=True,
        default='', null=True
    )
    end_time = DateTimeField(null=True, blank=True)
    time_taken = FloatField(blank=True, null=True)  # milliseconds
    encoded_headers = TextField(blank=True, default='')  # stores json
    meta_time = FloatField(null=True, blank=True)
    meta_num_queries = IntegerField(null=True, blank=True)
    meta_time_spent_queries = FloatField(null=True, blank=True)
    pyprofile = TextField(blank=True, default='')
    prof_file = FileField(max_length=300, blank=True, storage=silk_storage)

    # Useful method to create shortened copies of strings without losing start and end context
    # Used to ensure path and view_name don't exceed 190 characters
    def _shorten(self, string):
        return f'{string[:94]}...{string[len(string) - 93:]}'

    @property
    def total_meta_time(self):
        return (self.meta_time or 0) + (self.meta_time_spent_queries or 0)

    @property
    def profile_table(self):
        for n, columns in enumerate(parse_profile(self.pyprofile)):
            location = columns[-1]
            if n and '{' not in location and '<' not in location:
                r = re.compile(r'(?P<src>.*\.py)\:(?P<num>[0-9]+).*')
                m = r.search(location)
                group = m.groupdict()
                src = group['src']
                num = group['num']
                name = 'c%d' % n
                fmt = '<a name={name} href="?pos={n}&file_path={src}&line_num={num}#{name}">{location}</a>'
                rep = fmt.format(**dict(group, **locals()))
                yield columns[:-1] + [mark_safe(rep)]
            else:
                yield columns

    # defined in atomic transaction within SQLQuery save()/delete() as well
    # as in bulk_create of SQLQueryManager
    # TODO: This is probably a bad way to do this, .count() will prob do?
    num_sql_queries = IntegerField(default=0)  # TODO replace with count()

    @property
    def time_spent_on_sql_queries(self):
        """"
        Calculate the total time spent in milliseconds on SQL queries using Django aggregates.
        """
        result = SQLQuery.objects.filter(request=self).aggregate(
            total_time=Sum('time_taken', output_field=FloatField())
        )
        return result['total_time'] or 0.0

    @property
    def headers(self):
        if self.encoded_headers:
            raw = json.loads(self.encoded_headers)
        else:
            raw = {}

        return CaseInsensitiveDictionary(raw)

    @property
    def content_type(self):
        return self.headers.get('content-type', None)

    @classmethod
    def garbage_collect(cls, force=False):
        """ Remove Request/Responses when we are at the SILKY_MAX_RECORDED_REQUESTS limit
        Note that multiple in-flight requests may call this at once causing a
        double collection """
        check_percent = SilkyConfig().SILKY_MAX_RECORDED_REQUESTS_CHECK_PERCENT
        check_percent /= 100.0
        if check_percent < random.random() and not force:
            return
        target_count = SilkyConfig().SILKY_MAX_RECORDED_REQUESTS

        # Since garbage collection is probabilistic, the target count should
        # be lowered to account for requests before the next garbage collection
        if check_percent != 0:
            target_count -= int(1 / check_percent)

        # Make sure we can delete everything if needed by settings
        if target_count <= 0:
            cls.objects.all().delete()
            return

        try:
            time_cutoff = cls.objects.order_by(
                '-start_time'
            ).values_list(
                'start_time',
                flat=True
            )[target_count]
        except IndexError:
            return

        cls.objects.filter(start_time__lte=time_cutoff).delete()

    def save(self, *args, **kwargs):
        # sometimes django requests return the body as 'None'
        if self.raw_body is None:
            self.raw_body = ''

        if self.body is None:
            self.body = ''

        if self.end_time and self.start_time:
            interval = self.end_time - self.start_time
            self.time_taken = interval.total_seconds() * 1000

        # We can't save if either path or view_name exceed 190 characters
        if self.path and len(self.path) > 190:
            self.path = self._shorten(self.path)

        if self.view_name and len(self.view_name) > 190:
            self.view_name = self._shorten(self.view_name)

        super().save(*args, **kwargs)
        Request.garbage_collect(force=False)

    def summary_view(request):
    num_requests = Request.objects.count()
    avg_overall_time = Request.objects.aggregate(Avg('time_taken'))['time_taken__avg'] or 0
    avg_num_queries = Request.objects.aggregate(Avg('meta_num_queries'))['meta_num_queries__avg'] or 0
    avg_time_spent_on_queries = Request.objects.aggregate(Avg('meta_time_spent_queries'))['meta_time_spent_queries__avg'] or 0

    longest_queries_by_view = Request.objects.order_by('-time_taken')[:10]
    most_time_spent_in_db = Request.objects.order_by('-meta_time_spent_queries')[:10]
    most_queries = Request.objects.order_by('-meta_num_queries')[:10]

    options_view_style = [{'value': 'row', 'label': 'Row'}, {'value': 'grid', 'label': 'Grid'}]
    options_show = [25, 50, 100]
    options_order_by = [{'value': 'start_time', 'label': 'Start Time'}, {'value': 'time_taken', 'label': 'Time Taken'}]
    options_order_dir = [{'value': 'asc', 'label': 'Ascending'}, {'value': 'desc', 'label': 'Descending'}]

    context = {
        'num_requests': num_requests,
        'avg_overall_time': avg_overall_time,
        'avg_num_queries': avg_num_queries,
        'avg_time_spent_on_queries': avg_time_spent_on_queries,
        'longest_queries_by_view': longest_queries_by_view,
        'most_time_spent_in_db': most_time_spent_in_db,
        'most_queries': most_queries,
        'view_style': request.GET.get('view_style', 'row'),
        'show': request.GET.get('show', 25),
        'order_by': request.GET.get('order_by', 'start_time'),
        'order_dir': request.GET.get('order_dir', 'asc'),
        'options_view_style': options_view_style,
        'options_show': options_show,
        'options_order_by': options_order_by,
        'options_order_dir': options_order_dir,
    }

    return render(request, 'silk/summary.html', context)


class Response(models.Model):
    id = CharField(max_length=36, default=uuid4, primary_key=True)
    request = OneToOneField(
        Request, related_name='response', db_index=True,
        on_delete=models.CASCADE,
    )
    status_code = IntegerField()
    raw_body = TextField(blank=True, default='')
    body = TextField(blank=True, default='')
    encoded_headers = TextField(blank=True, default='')

    @property
    def content_type(self):
        return self.headers.get('content-type', None)

    @property
    def headers(self):
        if self.encoded_headers:
            raw = json.loads(self.encoded_headers)
        else:
            raw = {}
        return CaseInsensitiveDictionary(raw)

    @property
    def raw_body_decoded(self):
        return base64.b64decode(self.raw_body)


# TODO rewrite docstring
class SQLQueryManager(models.Manager):
    @transaction.atomic
    def bulk_create(self, *args, **kwargs):
        """ensure that num_sql_queries remains consistent. Bulk create does not call
        the model save() method and hence we must add this logic here too"""
        if len(args):
            objs = args[0]
        else:
            objs = kwargs.get('objs')
        for obj in objs:
            obj.prepare_save()

        return super().bulk_create(*args, **kwargs)


class SQLQuery(models.Model):
    query = TextField()
    start_time = DateTimeField(null=True, blank=True, default=timezone.now)
    end_time = DateTimeField(null=True, blank=True)
    time_taken = FloatField(blank=True, null=True)  # milliseconds
    identifier = IntegerField(default=-1)
    request = ForeignKey(
        Request, related_name='queries', null=True,
        blank=True, db_index=True, on_delete=models.CASCADE,
    )
    traceback = TextField()
    analysis = TextField(null=True, blank=True)
    objects = SQLQueryManager()

    # TODO docstring
    @property
    def traceback_ln_only(self):
        return '\n'.join(self.traceback.split('\n')[::2])

    @property
    def formatted_query(self):
        return sqlparse.format(self.query, reindent=True, keyword_case='upper')

    @property
    def num_joins(self):
        parsed_query = sqlparse.parse(self.query)
        count = 0
        for statement in parsed_query:
            count += sum(map(lambda t: t.match(sqlparse.tokens.Keyword, r'\.*join\.*', regex=True), statement.flatten()))
        return count

    @property
    def first_keywords(self):
        parsed_query = sqlparse.parse(self.query)
        keywords = []
        for statement in parsed_query[0].tokens:
            if not statement.is_keyword:
                break
            keywords.append(statement.value)
        return ' '.join(keywords)

    @property
    def tables_involved(self):
        """
        A really another rudimentary way to work out tables involved in a
        query.
        TODO: Can probably parse the SQL using sqlparse etc and pull out table
        info that way?
        """
        components = [x.strip() for x in self.query.split()]
        tables = []

        for idx, component in enumerate(components):
            # TODO: If django uses aliases on column names they will be falsely
            # identified as tables...
            if (
                component.lower() == "from"
                or component.lower() == "join"
                or component.lower() == "as"
                or component.lower() == "update"
            ):
                try:
                    _next = components[idx + 1]
                    if not _next.startswith('('):  # Subquery
                        stripped = _next.strip().strip(',')

                        if stripped:
                            tables.append(stripped)
                except IndexError:  # Reach the end
                    pass
        return tables

    def prepare_save(self):
        if self.end_time and self.start_time:
            interval = self.end_time - self.start_time
            self.time_taken = interval.total_seconds() * 1000

        if not self.pk:
            if self.request:
                self.request.num_sql_queries += 1
                self.request.save(update_fields=['num_sql_queries'])

    @transaction.atomic()
    def save(self, *args, **kwargs):
        self.prepare_save()
        super().save(*args, **kwargs)

    @transaction.atomic()
    def delete(self, *args, **kwargs):
        self.request.num_sql_queries -= 1
        self.request.save()
        super().delete(*args, **kwargs)


class BaseProfile(models.Model):
    name = CharField(max_length=300, blank=True, default='')
    start_time = DateTimeField(default=timezone.now)
    end_time = DateTimeField(null=True, blank=True)
    request = ForeignKey(
        Request, null=True, blank=True, db_index=True,
        on_delete=models.CASCADE,
    )
    time_taken = FloatField(blank=True, null=True)  # milliseconds

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if self.end_time and self.start_time:
            interval = self.end_time - self.start_time
            self.time_taken = interval.total_seconds() * 1000
        super().save(*args, **kwargs)


class Profile(BaseProfile):
    file_path = CharField(max_length=300, blank=True, default='')
    line_num = IntegerField(null=True, blank=True)
    end_line_num = IntegerField(null=True, blank=True)
    func_name = CharField(max_length=300, blank=True, default='')
    exception_raised = BooleanField(default=False)
    queries = ManyToManyField(SQLQuery, related_name='profiles', db_index=True)
    dynamic = BooleanField(default=False)

    @property
    def is_function_profile(self):
        return self.func_name is not None

    @property
    def is_context_profile(self):
        return self.func_name is None

    @property
    def time_spent_on_sql_queries(self):
        """
        Calculate the total time spent in milliseconds on SQL queries using Django aggregates.
        """
        result = self.queries.aggregate(
            total_time=Sum('time_taken', output_field=FloatField())
        )
        return result['total_time'] or 0.0
