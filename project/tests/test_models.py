# -*- coding: utf-8 -*-
import datetime
import uuid
import pytz

from django.test import TestCase
from django.utils import timezone


from freezegun import freeze_time

from silk import models
from silk.storage import ProfilerResultStorage
from silk.config import SilkyConfig
from .factories import RequestMinFactory, SQLQueryFactory, ResponseFactory


# TODO test atomicity

# http://stackoverflow.com/questions/13397038/uuid-max-character-length
# UUID_MAX_LENGTH = 36

# TODO move to separate file test and collection it self
class CaseInsensitiveDictionaryTest(object):
    pass


class RequestTest(TestCase):

    def setUp(self):

        self.obj = RequestMinFactory.create()
        self.max_percent = SilkyConfig().SILKY_MAX_RECORDED_REQUESTS_CHECK_PERCENT
        self.max_requests = SilkyConfig().SILKY_MAX_RECORDED_REQUESTS

    def tearDown(self):

        SilkyConfig().SILKY_MAX_RECORDED_REQUESTS_CHECK_PERCENT = self.max_percent
        SilkyConfig().SILKY_MAX_RECORDED_REQUESTS = self.max_requests

    def test_uuid_is_primary_key(self):

        self.assertIsInstance(self.obj.id, uuid.UUID)

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

    def test_garbage_collect(self):

        self.assertTrue(models.Request.objects.filter(id=self.obj.id).exists())
        SilkyConfig().SILKY_MAX_RECORDED_REQUESTS_CHECK_PERCENT = 100
        SilkyConfig().SILKY_MAX_RECORDED_REQUESTS = 0
        models.Request.garbage_collect()
        self.assertFalse(models.Request.objects.filter(id=self.obj.id).exists())

    def test_probabilistic_garbage_collect(self):

        self.assertTrue(models.Request.objects.filter(id=self.obj.id).exists())
        SilkyConfig().SILKY_MAX_RECORDED_REQUESTS_CHECK_PERCENT = 0
        SilkyConfig().SILKY_MAX_RECORDED_REQUESTS = 0
        models.Request.garbage_collect()
        self.assertTrue(models.Request.objects.filter(id=self.obj.id).exists())

    def test_force_garbage_collect(self):

        self.assertTrue(models.Request.objects.filter(id=self.obj.id).exists())
        SilkyConfig().SILKY_MAX_RECORDED_REQUESTS_CHECK_PERCENT = 0
        SilkyConfig().SILKY_MAX_RECORDED_REQUESTS = 0
        models.Request.garbage_collect(force=True)
        self.assertFalse(models.Request.objects.filter(id=self.obj.id).exists())

    def test_greedy_garbage_collect(self):

        for x in range(3):
            obj = models.Request(path='/', method='get')
            obj.save()
        self.assertEqual(models.Request.objects.count(), 4)
        SilkyConfig().SILKY_MAX_RECORDED_REQUESTS_CHECK_PERCENT = 50
        SilkyConfig().SILKY_MAX_RECORDED_REQUESTS = 3
        models.Request.garbage_collect(force=True)
        self.assertEqual(models.Request.objects.count(), 1)

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

    def test_prof_file_default_storage(self):
        obj = models.Request(path='/some/path/', method='get')
        self.assertEqual(obj.prof_file.storage.__class__, ProfilerResultStorage)


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

    def test_if_no_args_passed(self):
        pass
    def test_if_one_arg_passed(self):
        pass
    def if_a_few_args_passed(self):
        pass
    def if_objs_kw_arg_passed(self):
        pass
    def if_not_the_objs_kw_arg_passed(self):
        pass


class SQLQueryTest(TestCase):

    def setUp(self):

        self.obj = SQLQueryFactory.create()
        self.end_time = datetime.datetime(2016, 1, 1, 12, 0, 5, tzinfo=pytz.UTC)
        self.start_time = datetime.datetime(2016, 1, 1, 12, 0, 0, tzinfo=pytz.UTC)

    @freeze_time('2016-01-01 12:00:00')
    def test_start_time_field_default(self):

        obj = SQLQueryFactory.create()
        self.assertEqual(obj.start_time, datetime.datetime(2016, 1, 1, 12, 0, 0, tzinfo=pytz.UTC))

    def test_is_m2o_related_to_request(self):

        request = RequestMinFactory()
        self.obj.request = request
        self.obj.save()

        self.assertIn(self.obj, request.queries.all())

    def test_query_manager_instance(self):

        self.assertIsInstance(models.SQLQuery.objects, models.SQLQueryManager)

    def test_traceback_ln_only(self):

        self.obj.traceback = """Traceback (most recent call last):
          File "/home/user/some_script.py", line 10, in some_func
            pass
          File "/usr/lib/python2.7/bdb.py", line 20, in trace_dispatch
            return self.dispatch_return(frame, arg)
          File "/usr/lib/python2.7/bdb.py", line 30, in dispatch_return
            if self.quitting: raise BdbQuit
        BdbQuit"""

        output = ('Traceback (most recent call last):\n'
                  '            pass\n'
                  '            return self.dispatch_return(frame, arg)\n'
                  '            if self.quitting: raise BdbQuit')

        self.assertEqual(self.obj.traceback_ln_only, output)

    def test_formatted_query_if_no_query(self):

        self.obj.query = ""
        self.obj.formatted_query

    def test_formatted_query_if_has_a_query(self):

        query = """SELECT Book.title AS Title,
             COUNT(*) AS Authors
             FROM  Book
             JOIN  Book_author
                 ON  Book.isbn = Book_author.isbn
             GROUP BY Book.title;"""

        self.obj.query = query
        self.obj.formatted_query

    def test_num_joins_if_no_joins_in_query(self):

        query = """SELECT Book.title AS Title,
             COUNT(*) AS Authors
             FROM  Book
             GROUP BY Book.title;"""

        self.obj.query = query

        self.assertEqual(self.obj.num_joins, 0)

    def test_num_joins_if_joins_in_query(self):

        query = """SELECT p.id
                   FROM Person p
                       JOIN address a ON p.Id = a.Person_ID
                       JOIN address_type at ON a.Type_ID = at.Id
                       JOIN `option` o ON p.Id = o.person_Id
                       JOIN option_address_type oat ON o.id = oat.option_id
                    WHERE a.country_id = 1 AND at.id <> oat.type_id;"""

        self.obj.query = query
        self.assertEqual(self.obj.num_joins, 4)

    def test_num_joins_if_no_joins_in_query_but_this_word_searched(self):

        query = """SELECT Book.title FROM  Book WHERE Book.title=`Join the dark side, Luke!`;"""

        self.obj.query = query
        self.assertEqual(self.obj.num_joins, 0)

    def test_num_joins_if_multiple_statement_in_query(self):
        query = """SELECT Book.title FROM  Book WHERE Book.title=`Join the dark side, Luke!`;
                   SELECT Book.joiner FROM Book
                    LEFT OUTER JOIN joined ON Book.joiner = joined.joiner
                    INNER JOIN joined ON Book.joiner = joined.joiner
                   WHERE Book.joiner='Join i am'"""

        self.obj.query = query
        self.assertEqual(self.obj.num_joins, 2)

    def test_tables_involved_if_no_query(self):

        self.obj.query = ''

        self.assertEqual(self.obj.tables_involved, [])

    def test_tables_involved_if_query_has_only_a_from_token(self):

        query = """SELECT * FROM  Book;"""
        self.obj.query = query
        self.assertEqual(self.obj.tables_involved, ['Book;'])

    def test_tables_involved_if_query_has_a_join_token(self):

        query = """SELECT p.id FROM Person p JOIN Address a ON p.Id = a.Person_ID;"""
        self.obj.query = query
        self.assertEqual(self.obj.tables_involved, ['Person', 'Address'])

    def test_tables_involved_if_query_has_an_as_token(self):

        query = 'SELECT Book.title AS Title FROM  Book GROUP BY Book.title;'
        self.obj.query = query
        self.assertEqual(self.obj.tables_involved, ['Title', 'Book'])

    # FIXME bug, not a feature
    def test_tables_involved_check_with_fake_a_from_token(self):

        query = """SELECT * FROM  Book WHERE Book.title=`EVIL FROM WITHIN`;"""
        self.obj.query = query
        self.assertEqual(self.obj.tables_involved, ['Book', 'WITHIN`;'])

    # FIXME bug, not a feature
    def test_tables_involved_check_with_fake_a_join_token(self):

        query = """SELECT * FROM  Book WHERE Book.title=`Luke, join the dark side!`;"""
        self.obj.query = query
        self.assertEqual(self.obj.tables_involved, ['Book', 'the'])

    # FIXME bug, not a feature
    def test_tables_involved_check_with_fake_an_as_token(self):

        query = """SELECT * FROM  Book WHERE Book.title=`AS SOON AS POSIABLE`;"""
        self.obj.query = query
        self.assertEqual(self.obj.tables_involved, ['Book', 'POSIABLE`;'])

    def test_tables_involved_if_query_has_subquery(self):

        query = '''SELECT A.Col1, A.Col2, B.Col1,B.Col2
                  FROM (SELECT RealTableZ.Col1, RealTableY.Col2, RealTableY.ID AS ID
                          FROM RealTableZ
                               LEFT OUTER JOIN RealTableY ON RealTableZ.ForeignKeyY=RealTableY.ID
                         WHERE RealTableY.Col11>14
                        ) AS B INNER JOIN A
                ON A.ForeignKeyY=B.ID;'''
        self.obj.query = query
        self.assertEqual(self.obj.tables_involved, ['ID', 'RealTableZ', 'RealTableY', 'B', 'A'])

    # FIXME bug, not a feature
    def test_tables_involved_if_query_has_django_aliase_on_column_names(self):

        query = 'SELECT foo AS bar FROM some_table;'
        self.obj.query = query
        self.assertEqual(self.obj.tables_involved, ['bar', 'some_table;'])

    def test_save_if_no_end_and_start_time(self):

        obj = SQLQueryFactory.create()

        self.assertEqual(obj.time_taken, None)

    @freeze_time('2016-01-01 12:00:00')
    def test_save_if_has_end_time(self):

        # datetime.datetime(2016, 1, 1, 12, 0, 5, tzinfo=pytz.UTC)
        obj = SQLQueryFactory.create(end_time=self.end_time)

        self.assertEqual(obj.time_taken, 5000.0)

    @freeze_time('2016-01-01 12:00:00')
    def test_save_if_has_start_time(self):

        obj = SQLQueryFactory.create(start_time=self.start_time)

        self.assertEqual(obj.time_taken, None)

    def test_save_if_has_end_and_start_time(self):

        obj = SQLQueryFactory.create(start_time=self.start_time, end_time=self.end_time)

        self.assertEqual(obj.time_taken, 5000.0)

    def test_save_if_has_pk_and_request(self):

        self.obj.request = RequestMinFactory.create()
        self.obj.save()
        self.assertEqual(self.obj.request.num_sql_queries, 0)

    def test_save_if_has_no_pk(self):

        obj = SQLQueryFactory.build(start_time=self.start_time, end_time=self.end_time)
        obj.request = RequestMinFactory.create()
        obj.save()
        self.assertEqual(obj.request.num_sql_queries, 1)

    # should not rise
    def test_save_if_has_no_request(self):

        obj = SQLQueryFactory.build(start_time=self.start_time, end_time=self.end_time)
        obj.save()

    # FIXME a bug
    def test_delete_if_no_related_requests(self):

        with self.assertRaises(AttributeError):
            self.obj.delete()

        # self.assertNotIn(self.obj, models.SQLQuery.objects.all())

    def test_delete_if_has_request(self):

        self.obj.request = RequestMinFactory.create()
        self.obj.save()
        self.obj.delete()

        self.assertNotIn(self.obj, models.SQLQuery.objects.all())


class BaseProfileTest(TestCase):
    pass


class ProfileTest(TestCase):
    pass
