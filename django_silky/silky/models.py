from collections import Counter

from django.db import models
from django.db.models import DateTimeField, TextField, CharField, ForeignKey, IntegerField, BooleanField, F, \
    ManyToManyField
from django.utils import timezone
from django.db import transaction
import sqlparse


def time_taken(self):
    d = self.end_time - self.start_time
    return 0.0 + d.seconds * 1000 + d.microseconds / 1000


class Request(models.Model):
    view = CharField(max_length=300, db_index=True, blank=True, default='')
    path = CharField(max_length=300, db_index=True)
    query_params = TextField(blank=True, default='')
    body = TextField(blank=True, default='')
    method = CharField(max_length=10)
    start_time = DateTimeField(default=timezone.now)
    end_time = DateTimeField(null=True, blank=True)
    content_type = CharField(max_length=50)

    # defined in atomic transaction within SQLQuery save()/delete() as well
    # as in bulk_create of SQLQueryManager
    num_sql_queries = IntegerField(default=0)

    time_taken = property(time_taken)

    @property
    def time_spent_on_sql_queries(self):
        # TODO: Perhaps there is a nicer way to do this with Django aggregates?
        # My initial thought was to perform:
        #   SQLQuery.objects.filter.aggregate(Sum(F('end_time')) - Sum(F('start_time')))
        # However this feature isnt available yet, however there has been talk for use of F objects
        # within aggregates for four years here: https://code.djangoproject.com/ticket/14030
        # It looks like this will go in soon at which point this should be changed.
        return sum(x.time_taken for x in SQLQuery.objects.filter(request=self))


class SQLQueryManager(models.Manager):
    def bulk_create(self, *args, **kwargs):
        """ensure that num_sql_queries remains consistent. Bulk create does not call
        the model save() method and hence we must add this logic here too"""
        if len(args):
            objs = args[0]
        else:
            objs = kwargs.get('objs')
        with transaction.atomic():
            request_counter = Counter([x.request_id for x in objs])
            requests = Request.objects.filter(pk__in=request_counter.keys())
            # TODO: Not that there is ever more than one request (but there could be eventually)
            # but perhaps there is a cleaner way of apply the increment from the counter without iterating
            # and saving individually? e.g. bulk update but with diff. increments. Couldn't come up with this
            # off hand. --Mike
            for r in requests:
                r.num_sql_queries = F('num_sql_queries') + request_counter[r.pk]
                r.save()
            save = super(SQLQueryManager, self).bulk_create(*args, **kwargs)
            return save


class SQLQuery(models.Model):
    query = TextField()
    start_time = DateTimeField(null=True, blank=True, default=timezone.now)
    end_time = DateTimeField(null=True, blank=True)
    request = ForeignKey('Request', related_name='queries', null=True, blank=True)
    traceback = TextField()
    objects = SQLQueryManager()

    @property
    def traceback_ln_only(self):
        return '\n'.join(self.traceback.split('\n')[::2])

    @property
    def formatted_query(self):
        return sqlparse.format(self.query, reindent=True, keyword_case='upper')

    time_taken = property(time_taken)

    @transaction.atomic()
    def save(self, *args, **kwargs):
        if not self.pk:
            if self.request:
                self.request.num_sql_queries += 1
                self.request.save()
        super(SQLQuery, self).save(*args, **kwargs)

    @transaction.atomic()
    def delete(self, *args, **kwargs):
        self.request.num_sql_queries -= 1
        self.request.save()
        super(SQLQuery, self).delete(*args, **kwargs)


class BaseProfile(models.Model):
    name = CharField(max_length=300, blank=True)
    start_time = DateTimeField(default=timezone.now)
    end_time = DateTimeField(null=True, blank=True)
    request = ForeignKey('Request')
    time_taken = property(time_taken)

    class Meta:
        abstract = True


class Profile(BaseProfile):
    file_path = CharField(max_length=300, blank=True)
    line_num = IntegerField(null=True, blank=True)
    func_name = CharField(max_length=300, blank=True)
    exception_raised = BooleanField(default=False)
    queries = ManyToManyField('SQLQuery')

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
