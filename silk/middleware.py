import logging

from django.core.urlresolvers import reverse, NoReverseMatch

from django.db.models.sql.compiler import SQLCompiler
from django.utils import timezone

from silk.collector import DataCollector

from silk.config import SilkyConfig
from silk.model_factory import RequestModelFactory, ResponseModelFactory
from silk.models import _time_taken
from silk.profiling import dynamic
from silk.profiling.profiler import silk_meta_profiler
from silk.sql import execute_sql


Logger = logging.getLogger('silk')


def silky_reverse(name, *args, **kwargs):
    try:
        r = reverse('silk:%s' % name, *args, **kwargs)
    except NoReverseMatch:
        # In case user forgets to set namespace, but also fixes Django 1.5 tests on Travis
        # Hopefully if user has forgotten to add namespace there are no clashes with their own
        # view names but I don't think there is really anything can do about this.
        r = reverse(name, *args, **kwargs)
    return r


def _should_intercept(request):
    """we want to avoid recording any requests/sql queries etc that belong to Silky"""
    fpath = silky_reverse('requests')
    path = '/'.join(fpath.split('/')[0:-1])
    silky = request.path.startswith(path)
    ignored = request.path in SilkyConfig().SILKY_IGNORE_PATHS
    return not (silky or ignored)


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

    @silk_meta_profiler()
    def process_request(self, request):
        request_model = None
        if _should_intercept(request):
            self._apply_dynamic_mappings()
            if not hasattr(SQLCompiler, '_execute_sql'):
                SQLCompiler._execute_sql = SQLCompiler.execute_sql
                SQLCompiler.execute_sql = execute_sql
            request_model = RequestModelFactory(request).construct_request_model()
        DataCollector().configure(request_model)

    def _process_response(self, response):
        with silk_meta_profiler():
            collector = DataCollector()
            silk_request = collector.request
            if silk_request:
                silk_response = ResponseModelFactory(response).construct_response_model()
                silk_response.save()
                silk_request.end_time = timezone.now()
                collector.finalise()
            else:
                Logger.error('No request model was available when processing response. Did something go wrong in process_request/process_view?')
        silk_request.save()

    def process_response(self, request, response):
        if _should_intercept(request):
            self._process_response(response)
        return response