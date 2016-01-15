# -*- coding: utf-8 -*-
import factory
import factory.fuzzy

from silk.models import Request, SQLQuery


HTTP_METHODS = ['GET', 'POST', 'PUT', 'PATCH', 'HEAD', 'OPTIONS']


class SQLQueryFactory(factory.django.DjangoModelFactory):

    query = factory.Sequence(lambda num: u'SELECT foo FROM bar WHERE foo=%s' % num)
    # end_time = DateTimeField(null=True, blank=True)
    # time_taken = FloatField(blank=True, null=True)
    # request = ForeignKey('Request', related_name='queries', null=True, blank=True, db_index=True)
    traceback = factory.Sequence(lambda num: u'Traceback #%s' % num)

    class Meta:
        model = SQLQuery


class RequestMinFactory(factory.django.DjangoModelFactory):
    # email = factory.LazyAttribute(lambda o: '%s@example.org' % o.username)
    # first_name = factory.Sequence(lambda i: 'first_name%s' % i)
    # is_active = True
    # is_valid_email = True
    # last_name = factory.Sequence(lambda i: 'last_name%s' % i)
    # password = factory.PostGenerationMethodCall('set_password', 'defaultpassword')
    # username = factory.Sequence(lambda i: 'username%s' % i)

    path = factory.Faker('uri_path')
    method = factory.fuzzy.FuzzyChoice(HTTP_METHODS)
    # start_time = DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        model = Request
        # exclude = (,)


# class RequestMaxFactory(RequestMinFactory):

#     query_params = TextField(blank=True, default='')
#     raw_body = TextField(blank=True, default='')
#     body = TextField(blank=True, default='')
#     view_name = CharField(max_length=300, db_index=True, blank=True, default='', null=True)
#     end_time = DateTimeField(null=True, blank=True)
#     time_taken = FloatField(blank=True, null=True)
#     encoded_headers = TextField(blank=True, default='')
#     meta_time = FloatField(null=True, blank=True)
#     meta_num_queries = IntegerField(null=True, blank=True)
#     meta_time_spent_queries = FloatField(null=True, blank=True)
#     pyprofile = TextField(blank=True, default='')
