from collections import Counter
import json

from django.db import models
from django.db.models import DateTimeField, TextField, CharField, ForeignKey, IntegerField, BooleanField, F, \
    ManyToManyField, OneToOneField, FloatField
from django.utils import timezone
from django.db import transaction
import sqlparse


# Seperated out so can use in tests w/o models
def _time_taken(start_time, end_time):
    d = end_time - start_time
    return d.seconds * 1000 + d.microseconds / 1000


def time_taken(self):
    return _time_taken(self.start_time, self.end_time)


class CaseInsensitiveDictionary(dict):
    def __getitem__(self, key):
        return super(CaseInsensitiveDictionary, self).__getitem__(key.lower())

    def __setitem__(self, key, value):
        super(CaseInsensitiveDictionary, self).__setitem__(key.lower(), value)

    def update(self, other=None, **kwargs):
        for k, v in other.items():
            self[k] = v
        for k, v in kwargs.items():
            self[k] = v

    def __init__(self, d):
        super(CaseInsensitiveDictionary, self).__init__()
        for k, v in d.items():
            self[k] = v


class Request(models.Model):
    path = CharField(max_length=300, db_index=True)
    query_params = TextField(blank=True, default='')
    raw_body = TextField(blank=True, default='')
    body = TextField(blank=True, default='')
    method = CharField(max_length=10)
    start_time = DateTimeField(default=timezone.now)
    end_time = DateTimeField(null=True, blank=True)
    time_taken = FloatField(blank=True, null=True)
    encoded_headers = TextField(blank=True, default='')
    meta_time = FloatField(null=True, blank=True)
    meta_num_queries = IntegerField(null=True, blank=True)
    meta_time_spent_queries = FloatField(null=True, blank=True)

    @property
    def total_meta_time(self):
        return (self.meta_time or 0) + (self.meta_time_spent_queries or 0)

    # defined in atomic transaction within SQLQuery save()/delete() as well
    # as in bulk_create of SQLQueryManager
    # TODO: This is probably a bad way to do this, .count() will prob do?
    num_sql_queries = IntegerField(default=0)


    @property
    def time_spent_on_sql_queries(self):
        # TODO: Perhaps there is a nicer way to do this with Django aggregates?
        # My initial thought was to perform:
        # SQLQuery.objects.filter.aggregate(Sum(F('end_time')) - Sum(F('start_time')))
        # However this feature isnt available yet, however there has been talk for use of F objects
        # within aggregates for four years here: https://code.djangoproject.com/ticket/14030
        # It looks like this will go in soon at which point this should be changed.
        return sum(x.time_taken for x in SQLQuery.objects.filter(request=self))

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

    def save(self, *args, **kwargs):
        if self.end_time and self.start_time:
            interval = self.end_time - self.start_time
            self.time_taken = interval.total_seconds() * 1000
        super(Request, self).save(*args, **kwargs)


class Response(models.Model):
    request = OneToOneField('Request', related_name='response')
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



class SQLQueryManager(models.Manager):
    def bulk_create(self, *args, **kwargs):
        """ensure that num_sql_queries remains consistent. Bulk create does not call
        the model save() method and hence we must add this logic here too"""
        if len(args):
            objs = args[0]
        else:
            objs = kwargs.get('objs')
        with transaction.commit_on_success():
            request_counter = Counter([x.request_id for x in objs])
            requests = Request.objects.filter(pk__in=request_counter.keys())
            # TODO: Not that there is ever more than one request (but there could be eventually)
            # but perhaps there is a cleaner way of apply the increment from the counter without iterating
            # and saving individually? e.g. bulk update but with diff. increments. Couldn't come up with this
            # off hand.
            for r in requests:
                r.num_sql_queries = F('num_sql_queries') + request_counter[r.pk]
                r.save()
            save = super(SQLQueryManager, self).bulk_create(*args, **kwargs)
            return save


class SQLQuery(models.Model):
    query = TextField()
    start_time = DateTimeField(null=True, blank=True, default=timezone.now)
    end_time = DateTimeField(null=True, blank=True)
    time_taken = FloatField(blank=True, null=True)
    request = ForeignKey('Request', related_name='queries', null=True, blank=True)
    traceback = TextField()
    objects = SQLQueryManager()

    @property
    def traceback_ln_only(self):
        return '\n'.join(self.traceback.split('\n')[::2])

    @property
    def formatted_query(self):
        return sqlparse.format(self.query, reindent=True, keyword_case='upper')

    # TODO: Surely a better way to handle this? May return false positives
    @property
    def num_joins(self):
        return self.query.lower().count('join ')

    @property
    def tables_involved(self):
        """A rreally ather rudimentary way to work out tables involved in a query.
        TODO: Can probably parse the SQL using sqlparse etc and pull out table info that way?"""
        components = [x.strip() for x in self.query.split()]
        tables = []
        for idx, c in enumerate(components):
            # TODO: If django uses aliases on column names they will be falsely identified as tables...
            if c.lower() == 'from' or c.lower() == 'join' or c.lower() == 'as':
                try:
                    nxt = components[idx + 1]
                    if not nxt.startswith('('):  # Subquery
                        stripped = nxt.strip().strip(',')
                        if stripped:
                            tables.append(stripped)
                except IndexError:  # Reach the end
                    pass
        return tables

    @transaction.commit_on_success()
    def save(self, *args, **kwargs):
        if self.end_time and self.start_time:
            interval = self.end_time - self.start_time
            self.time_taken = interval.total_seconds() * 1000
        if not self.pk:
            if self.request:
                self.request.num_sql_queries += 1
                self.request.save()
        super(SQLQuery, self).save(*args, **kwargs)

    @transaction.commit_on_success()
    def delete(self, *args, **kwargs):
        self.request.num_sql_queries -= 1
        self.request.save()
        super(SQLQuery, self).delete(*args, **kwargs)


class BaseProfile(models.Model):
    name = CharField(max_length=300, blank=True, default='')
    start_time = DateTimeField(default=timezone.now)
    end_time = DateTimeField(null=True, blank=True)
    request = ForeignKey('Request', null=True, blank=True)
    time_taken = FloatField(blank=True, null=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if self.end_time and self.start_time:
            interval = self.end_time - self.start_time
            self.time_taken = interval.total_seconds() * 1000
        super(BaseProfile, self).save(*args, **kwargs)


class Profile(BaseProfile):
    file_path = CharField(max_length=300, blank=True, default='')
    line_num = IntegerField(null=True, blank=True)
    end_line_num = IntegerField(null=True, blank=True)
    func_name = CharField(max_length=300, blank=True, default='')
    exception_raised = BooleanField(default=False)
    queries = ManyToManyField('SQLQuery', related_name='profiles')
    dynamic = BooleanField(default=False)

    @property
    def is_function_profile(self):
        return self.func_name is not None

    @property
    def is_context_profile(self):
        return self.func_name is None

    @property
    def time_spent_on_sql_queries(self):
        time_spent = sum(x.time_taken for x in self.queries.all())
        return time_spent
