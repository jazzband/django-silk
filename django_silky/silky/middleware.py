import inspect
import json
import logging
from django.db import IntegrityError

from django.db.models.sql.compiler import SQLCompiler
from django.utils import timezone
import six
from silky import models

from silky.collector import DataCollector
from silky.config import SilkyConfig
from silky.profiling import dynamic
from silky.sql import execute_sql

Logger = logging.getLogger('silky')


class SilkyMiddleware(object):
    content_types_json = ['application/json',
                          'application/x-javascript',
                          'text/javascript',
                          'text/x-javascript',
                          'text/x-json']
    content_type_form = ['multipart/form-data',
                         'application/x-www-form-urlencoded']
    content_type_html = ['text/html']
    content_type_css = ['text/css']

    def __init__(self):
        super(SilkyMiddleware, self).__init__()

    def _apply_dynamic_mappings(self):
        dynamic_profile_configs = SilkyConfig().SILKY_DYNAMIC_PROFILING
        for conf in dynamic_profile_configs:
            module = conf.get('module')
            function = conf.get('function')
            start_line = conf.get('start_line')
            end_line = conf.get('end_line')
            name = conf.get('name')
            if module and function:
                if start_line and end_line:  # Dynamic context manager
                    dynamic.inject_context_manager_func(module=module,
                                                        func=function,
                                                        start_line=start_line,
                                                        end_line=end_line,
                                                        name=name)
                else:  # Dynamic decorator
                    dynamic.profile_function_or_method(module=module,
                                                       func=function,
                                                       name=name)
            else:
                raise KeyError('Invalid dynamic mapping %s' % conf)

    def process_request(self, request):
        path = request.path
        if not request.path.startswith('/silky'):  # We dont want to profile requests to Silky. Shit would go down.
            self._apply_dynamic_mappings()
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
            request_model = models.Request.objects.create(path=path,
                                                          body=body,
                                                          method=request.method,
                                                          content_type=content_type,
                                                          query_params=encoded_query_params)
            DataCollector().request = request_model

    def process_view(self, request, view_func, *args, **kwargs):
        if not request.path.startswith('/silky'):
            try:
                func_name = view_func.__name__
            except AttributeError:  # e.g. in case of Django Syndication Feed
                func_name = view_func.__class__.__name__
            if inspect.ismethod(view_func):
                view_name = view_func.im_class.__module__ + '.' + view_func.im_class.__name__ + func_name
            else:
                view_name = view_func.__module__ + '.' + func_name
            current_request = DataCollector().request
            assert current_request, 'no request model available?'
            current_request.view = view_name

    def process_response(self, request, response):
        if not request.path.startswith('/silky'):
            collector = DataCollector()
            body = ''
            content_type = response['Content-Type'].split(';')[0]
            if content_type in self.content_types_json + ['text/plain'] + self.content_type_html + self.content_type_css:
                body = response.content
            try:  # TODO: This is called twice sometimes... Why?
                models.Response.objects.create(request=collector.request, status_code=response.status_code, content_type=content_type, body=body)
            except IntegrityError as e:
                Logger.error('Unable to save response due to %s. For some reason process_response sometimes gets called twice...?' % e)
            finally:
                collector.request.end_time = timezone.now()
                collector.request.save()
        return response
