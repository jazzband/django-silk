import Queue
import atexit
import inspect
import json

from django.db.models.sql.compiler import SQLCompiler
from django.utils import timezone

import models
from silky.local import DataCollector
from silky.sql import execute_sql
from silky.thread import SilkyThread


class SilkyMiddleware(object):
    """this bad boy is where all the magic happens. all the wrapping and writing
    things down to the database starts here"""
    content_types_json = ['application/json', 'application/x-javascript', 'text/javascript', 'text/x-javascript',
                          'text/x-json']
    content_type_form = ['multipart/form-data', 'application/x-www-form-urlencoded']

    def __init__(self):
        super(SilkyMiddleware, self).__init__()
        self.queue = Queue.Queue()
        # self.thread = SilkyThread(self.queue)
        # self.thread.start()
        # atexit.register(self.clean_up)

    def process_request(self, request):
        path = request.path
        if not request.path.startswith('/silky'):  # We dont want to profile requests to Silky. Shit would go down.
            if not hasattr(SQLCompiler, '_execute_sql'):
                SQLCompiler._execute_sql = SQLCompiler.execute_sql
                SQLCompiler.execute_sql = execute_sql
            body = ''
            content_type = request.META.get('CONTENT_TYPE', '')
            if content_type:
                content_type = content_type.split(';')[0]
            if content_type in self.content_type_form:
                body = request.POST
                body = json.dumps(dict(body))  # Encode as json
            elif content_type in self.content_types_json + ['text/plain']:
                body = request.body
            query_params = request.GET
            encoded_query_params = ''
            if query_params:
                query_params_dict = dict(zip(query_params.keys(), query_params.values()))
                encoded_query_params = json.dumps(query_params_dict)
            request_model = models.Request(path=path,
                                           body=body,
                                           method=request.method,
                                           content_type=content_type,
                                           query_params=encoded_query_params)
            DataCollector().configure(request_model)

    def process_view(self, request, view_func, view_args, view_kwargs):
        if not request.path.startswith('/silky'):
            if inspect.ismethod(view_func):
                view_name = view_func.im_class.__module__ + '.' + view_func.im_class.__name__ + view_func.__name__
            else:
                view_name = view_func.__module__ + '.' + view_func.__name__
            current_request = DataCollector().request
            assert current_request, 'no request model available?'
            current_request.view = view_name

    def save(self):
        collector = DataCollector()
        collector.request.end_time = timezone.now()
        collector.save()


    def process_response(self, request, response):
        if not request.path.startswith('/silky'):
            self.save()
        return response

    # def clean_up(self):
    #     self.thread.running = False
    #     self.thread.join()


