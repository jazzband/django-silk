import json
import os
import random
import traceback

from django.core import management
from django.utils import timezone

from silk import models
from silk.models import SQLQuery, Profile


class MockSuite(object):
    """
    Provides some fake data to play around with. Also useful for testing
    """
    methods = ['GET', 'POST', 'PUT', 'PATCH', 'HEAD', 'OPTIONS']
    path_components = ['path', 'to', 'somewhere', 'around', 'here', 'bobs', 'your', 'uncle']
    status_codes = [200, 201, 300, 301, 302, 403, 404, 500]
    profile_names = ['slow_bit_of_code', 'terrible_dependency', 'what_on_earth_is_this_code_doing']
    file_path = [os.path.realpath(__file__)]
    func_names = ['', '', '', 'foo', 'bar']
    view_names = ['app:blah', 'index', 'root', 'xxx:xyx']
    sql_queries = ['''
    SELECT Book.title AS Title,
    COUNT(*) AS Authors
     FROM  Book
     JOIN  Book_author
       ON  Book.isbn = Book_author.isbn
     GROUP BY Book.title;
 ''',
                   '''
    SELECT * FROM table
    ''', '''
    SELECT *
    FROM  Book
    WHERE price > 100.00
    ORDER BY title;
  ''', '''
  SELECT title,
       COUNT(*) AS Authors
 FROM  Book
 NATURAL JOIN Book_author
 GROUP BY title;
  ''',
                   '''
                   SELECT A.Col1, A.Col2, B.Col1,B.Col2
      FROM (SELECT RealTableZ.Col1, RealTableY.Col2, RealTableY.ID AS ID
              FROM RealTableZ
   LEFT OUTER JOIN RealTableY
                ON RealTableZ.ForeignKeyY=RealTableY.ID
             WHERE RealTableY.Col11>14
            ) AS B
        INNER JOIN A
                ON A.ForeignKeyY=B.ID
                   ''']

    response_content_types = ['text/html', 'application/json', 'text/css']
    response_content = {
        'text/html': ['<html></html>'],
        'text/css': ['#blah {font-weight: bold}'],
        'application/json': ['[1, 2, 3]']
    }
    request_content_types = ['application/json']
    request_content = {
        'application/json': ['{"blah": 5}']
    }

    def _random_method(self):
        return random.choice(self.methods)

    def _random_path(self):
        num_components = random.randint(1, 5)
        return '/' + '/'.join(random.sample(self.path_components, num_components)) + '/'

    def _random_query(self):
        return random.choice(self.sql_queries)

    def mock_sql_queries(self, request=None, profile=None, n=1, as_dict=False):
        start_time, end_time = self._random_time()
        queries = []
        for _ in range(0, n):
            tb = ''.join(reversed(traceback.format_stack()))
            d = {
                'query': self._random_query(),
                'start_time': start_time,
                'end_time': end_time,
                'request': request,
                'traceback': tb
            }
            if as_dict:
                queries.append(d)
            else:
                query = SQLQuery.objects.create(**d)
                queries.append(query)
        if profile:
            if as_dict:
                for q in queries:
                    profile['queries'].append(q)
            else:
                profile.queries.set(queries)
        return queries

    def mock_profile(self, request=None):
        start_time, end_time = self._random_time()
        dynamic = random.choice([True, False])
        profile = Profile.objects.create(start_time=start_time,
                                         end_time=end_time,
                                         request=request,
                                         name=random.choice(self.profile_names),
                                         file_path=random.choice(self.file_path),
                                         line_num=3,
                                         func_name=random.choice(self.func_names),
                                         dynamic=dynamic,
                                         end_line_num=6 if dynamic else None,
                                         exception_raised=random.choice([True, False])
        )
        self.mock_sql_queries(profile=profile, n=random.randint(0, 10))
        return profile

    def mock_profiles(self, request=None, n=1):
        profiles = []

        for _ in range(0, n):
            profile = self.mock_profile(request)
            profiles.append(profile)
        return profiles

    def _random_time(self):
        start_time = timezone.now()
        duration = timedelta(milliseconds=random.randint(0, 3000))
        end_time = start_time + duration
        return start_time, end_time

    def mock_request(self):
        start_time, end_time = self._random_time()
        num_sql_queries = random.randint(0, 20)
        request_content_type = random.choice(self.request_content_types)
        request_body = random.choice(self.request_content[request_content_type])
        time_taken = end_time - start_time
        time_taken = time_taken.total_seconds()
        request = models.Request.objects.create(method=self._random_method(),
                                                path=self._random_path(),
                                                num_sql_queries=num_sql_queries,
                                                start_time=start_time,
                                                end_time=end_time,
                                                view_name=random.choice(self.view_names),
                                                time_taken=time_taken,
                                                encoded_headers=json.dumps({'content-type': request_content_type}),
                                                body=request_body)
        response_content_type = random.choice(self.response_content_types)
        response_body = random.choice(self.response_content[response_content_type])
        models.Response.objects.create(request=request,
                                       status_code=random.choice(self.status_codes),
                                       encoded_headers=json.dumps({'content-type': response_content_type}),
                                       body=response_body)
        self.mock_sql_queries(request=request, n=num_sql_queries)
        self.mock_profiles(request, random.randint(0, 2))
        return request


if __name__ == '__main__':
    management.call_command('flush', interactive=False)
    requests = [MockSuite().mock_request() for _ in range(0, 100)]

