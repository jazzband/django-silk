# -*- coding: utf-8 -*-
import datetime
import uuid
import pytz

from django.test import TestCase
from django.utils import timezone


from freezegun import freeze_time

from silk import models
from .factories import RequestMinFactory, SQLQueryFactory, ResponseFactory


# http://stackoverflow.com/questions/13397038/uuid-max-character-length
# UUID_MAX_LENGTH = 36

# TODO move to separate file test and collection it self
class CaseInsensitiveDictionaryTest(object):
    pass


class RequestTest(TestCase):

    def setUp(self):

        self.obj = RequestMinFactory.create()

    def test_uuid_is_primary_key(self):

        self.assertIsInstance(self.obj.id, uuid.UUID)

    # 2016-01-13 16:08:11.531676+00:00
    @freeze_time('2016-01-01 12:00:00')
    def test_start_time_field_default(self):

        obj = RequestMinFactory.create()
        self.assertEqual(obj.start_time, datetime.datetime(2016, 1, 1, 12, 0, 0, tzinfo=pytz.UTC))

    def test_total_meta_time_if_have_no_meta_and_queries_time(self):

        self.assertEqual(self.obj.total_meta_time, 0)

    def test_total_meta_time_if_have_meta_time_spent_queries(self):

        obj = RequestMinFactory.create(meta_time_spent_queries=10.5)
        self.assertEqual(obj.total_meta_time, 10.5)

    def test_total_meta_time_if_meta_time(self):

        obj = RequestMinFactory.create(meta_time=3.3)
        self.assertEqual(obj.total_meta_time, 3.3)

    def test_total_meta_if_self_have_it_meta_and_queries_time(self):

        obj = RequestMinFactory.create(meta_time=3.3, meta_time_spent_queries=10.5)
        self.assertEqual(obj.total_meta_time, 13.8)

    def test_time_spent_on_sql_queries_if_has_no_related_SQLQueries(self):

        self.assertEqual(self.obj.time_spent_on_sql_queries, 0)

    # FIXME probably a bug
    def test_time_spent_on_sql_queries_if_has_related_SQLQueries_with_no_time_taken(self):

        query = SQLQueryFactory()
        self.obj.queries.add(query)

        self.assertEqual(query.time_taken, None)

        with self.assertRaises(TypeError):
            self.obj.time_spent_on_sql_queries

    def test_time_spent_on_sql_queries_if_has_related_SQLQueries_and_time_taken(self):

        query1 = SQLQueryFactory(time_taken=3.5)
        query2 = SQLQueryFactory(time_taken=1.5)
        self.obj.queries.add(query1, query2)

        self.assertEqual(self.obj.time_spent_on_sql_queries, 0)

    def test_time_spent_on_sql_queries_if_has_related_SQLQueries_and_time_taken(self):

        query1 = SQLQueryFactory(time_taken=3.5)
        query2 = SQLQueryFactory(time_taken=1.5)
        RequestMinFactory().queries.add(query1, query2)

        self.assertEqual(self.obj.time_spent_on_sql_queries, 0)

    def test_headers_if_has_no_encoded_headers(self):

        self.assertIsInstance(self.obj.headers, models.CaseInsensitiveDictionary)
        self.assertFalse(self.obj.headers)

    def test_headers_if_has_encoded_headers(self):

        self.obj.encoded_headers = '{"some-header": "some_data"}'
        self.assertIsInstance(self.obj.headers, models.CaseInsensitiveDictionary)
        self.assertDictEqual(self.obj.headers, {u'some-header': u'some_data'})

    def test_content_type_if_no_headers(self):

        self.assertEqual(self.obj.content_type, None)

    def test_content_type_if_no_specific_content_type(self):

        self.obj.encoded_headers = '{"foo": "some_data"}'
        self.assertEqual(self.obj.content_type, None)

    def test_content_type_if_header_have_content_type(self):

        self.obj.encoded_headers = '{"content-type": "some_data"}'
        self.assertEqual(self.obj.content_type, "some_data")

    def test_save_if_have_no_raw_body(self):

        obj = models.Request(path='/some/path/', method='get')
        self.assertEqual(obj.raw_body, '')
        obj.save()
        self.assertEqual(obj.raw_body, '')

    def test_save_if_have_raw_body(self):

        obj = models.Request(path='/some/path/', method='get', raw_body='some text')
        obj.save()
        self.assertEqual(obj.raw_body, u'some text')

    def test_save_if_have_no_body(self):

        obj = models.Request(path='/some/path/', method='get')
        self.assertEqual(obj.body, '')
        obj.save()
        self.assertEqual(obj.body, '')

    def test_save_if_have_body(self):

        obj = models.Request(path='/some/path/', method='get', body='some text')
        obj.save()
        self.assertEqual(obj.body, u'some text')

    def test_save_if_have_no_end_time(self):

        obj = models.Request(path='/some/path/', method='get')
        self.assertEqual(obj.time_taken, None)
        obj.save()
        self.assertEqual(obj.time_taken, None)

    @freeze_time('2016-01-01 12:00:00')
    def test_save_if_have_end_time(self):

        date = datetime.datetime(2016, 1, 1, 12, 0, 3, tzinfo=pytz.UTC)
        obj = models.Request(path='/some/path/', method='get', end_time=date)
        obj.save()
        self.assertEqual(obj.end_time, date)
        self.assertEqual(obj.time_taken, 3000.0)


class ResponseTest(TestCase):

    def setUp(self):

        self.obj = ResponseFactory.create()

    def test_uuid_is_primary_key(self):

        self.assertIsInstance(self.obj.id, uuid.UUID)

    def test_is_1to1_related_to_request(self):

        request = RequestMinFactory.create()
        resp = models.Response.objects.create(status_code=200, request=request)

        self.assertEqual(request.response, resp)

    def test_headers_if_has_no_encoded_headers(self):

        self.assertIsInstance(self.obj.headers, models.CaseInsensitiveDictionary)
        self.assertFalse(self.obj.headers)

    def test_headers_if_has_encoded_headers(self):

        self.obj.encoded_headers = '{"some-header": "some_data"}'
        self.assertIsInstance(self.obj.headers, models.CaseInsensitiveDictionary)
        self.assertDictEqual(self.obj.headers, {u'some-header': u'some_data'})

    def test_content_type_if_no_headers(self):

        self.assertEqual(self.obj.content_type, None)

    def test_content_type_if_no_specific_content_type(self):

        self.obj.encoded_headers = '{"foo": "some_data"}'
        self.assertEqual(self.obj.content_type, None)

    def test_content_type_if_header_have_content_type(self):

        self.obj.encoded_headers = '{"content-type": "some_data"}'
        self.assertEqual(self.obj.content_type, "some_data")


class SQLQueryManagerTest(TestCase):
    pass


class SQLQueryTest(TestCase):
    pass


class BaseProfileTest(TestCase):
    pass


class ProfileTest(TestCase):
    pass
