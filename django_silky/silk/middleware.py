import json
import logging

from django.core.urlresolvers import reverse
from django.db.models.sql.compiler import SQLCompiler
from django.utils import timezone

from silk import models
from silk.collector import DataCollector
from silk.config import SilkyConfig
from silk.profiling import dynamic
from silk.sql import execute_sql


Logger = logging.getLogger('silk')

content_types_json = ['application/json',
                      'application/x-javascript',
                      'text/javascript',
                      'text/x-javascript',
                      'text/x-json']
content_type_form = ['multipart/form-data',
                     'application/x-www-form-urlencoded']
content_type_html = ['text/html']
content_type_css = ['text/css']


def _should_intercept(request):
    """we want to avoid recording any requests/sql queries etc that belong to Silky"""
    path = reverse('silk:requests')
    should_intercept = not request.path.startswith(path)
    return should_intercept


class RequestModelFactory(object):
    """Produce Request models from Django request objects"""

    def __init__(self, request):
        super(RequestModelFactory, self).__init__()
        self.request = request

    def content_type(self):
        content_type = self.request.META.get('CONTENT_TYPE', '')
        if content_type:
            content_type = content_type.split(';')[0]
        return content_type

    def body(self):
        content_type = self.content_type()
        body = ''
        # Encode body as JSON if possible so can be used as a dictionary in generation
        # of curl/django test client code
        if content_type in content_type_form:
            body = self.request.POST
            body = json.dumps(dict(body), sort_keys=True, indent=4)
        elif content_type in content_types_json:
            # TODO: Perhaps theres a way to format the JSON without parsing it?
            body = json.dumps(json.loads(self.request.body), sort_keys=True, indent=4)
        return body, content_type

    def query_params(self):
        query_params = self.request.GET
        encoded_query_params = ''
        if query_params:
            query_params_dict = dict(zip(query_params.keys(), query_params.values()))
            encoded_query_params = json.dumps(query_params_dict)
        return encoded_query_params

    def construct_request_model(self):
        body, content_type = self.body()
        query_params = self.query_params()
        request_model = models.Request.objects.create(raw_body=self.request.body,
                                                      content_type=content_type,
                                                      path=self.request.path,
                                                      method=self.request.method,
                                                      query_params=query_params,
                                                      body=body)
        Logger.debug('Created new request model with pk %s' % request_model.pk)
        return request_model


class ResponseModelFactory(object):
    """Produce Request models from Django request objects"""


class SilkyMiddleware(object):
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
        if _should_intercept(request):
            self._apply_dynamic_mappings()
            if not hasattr(SQLCompiler, '_execute_sql'):
                SQLCompiler._execute_sql = SQLCompiler.execute_sql
                SQLCompiler.execute_sql = execute_sql
            request_model = RequestModelFactory(request).construct_request_model()
            DataCollector().configure(request_model)

    def process_response(self, request, response):
        if _should_intercept(request):
            collector = DataCollector()
            content_type = response['Content-Type'].split(';')[0]
            silk_request = collector.request
            if silk_request:
                Logger.debug('Creating response model for request model with pk %s' % silk_request.pk)
                body = ''
                if content_type in content_types_json:
                    # TODO: Perhaps theres a way to format the JSON without parsing it?
                    try:
                        content = response.content
                        try:  #py3
                            content = content.decode('UTF-8')
                        except AttributeError:  #py2
                            pass
                        body = json.dumps(json.loads(content), sort_keys=True, indent=4)
                    except (TypeError, ValueError):
                        Logger.warn('Response to request with pk %s has content type %s but was unable to parse it' % (silk_request.pk, content_type))
                models.Response.objects.create(request=silk_request,
                                               status_code=response.status_code,
                                               content_type=content_type,
                                               raw_body=response.content,
                                               body=body)
                silk_request.end_time = timezone.now()
                silk_request.save()
                collector.finalise()
            else:
                Logger.error('No request model was available when processing response. Did something go wrong in process_request/process_view?')
        return response