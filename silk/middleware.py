import importlib
import logging
import random
import types

from django.core.urlresolvers import reverse, NoReverseMatch

from django.db.models.sql.compiler import SQLCompiler
from django.utils import timezone

from silk.collector import DataCollector

from silk.config import SilkyConfig
from silk.model_factory import RequestModelFactory, ResponseModelFactory
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


fpath = silky_reverse('summary')
config = SilkyConfig()


class TestMiddleware(object):

    def process_response(self, request, response):
        return response

    def process_request(self, request):
        return


def _sample_intercepts(request):
    # don't trap every request
    if config.SILKY_INTERCEPT_PERCENT < 100:
        if random.random() > config.SILKY_INTERCEPT_PERCENT / 100.0:
            return False


class SilkyMiddleware(object):

    def __init__(self):
        super(SilkyMiddleware, self).__init__()
        if config.SILKY_INTERCEPT_FUNC and type(config.SILKY_INTERCEPT_FUNC) == str:
            # Dynamically load the custom intercept function here so we
            # only pay the cost once for this process.
            func_path = config.SILKY_INTERCEPT_FUNC
            # Replace this with import_by_path in when minimum
            # supported Django version >= 1.6.
            mod_path, func_name = func_path.rsplit('.', 1)
            custom_func = getattr(importlib.import_module(mod_path), func_name)
            self._custom_should_intercept = custom_func
        elif (config.SILKY_INTERCEPT_FUNC and
              type(config.SILKY_INTERCEPT_FUNC) == types.FunctionType):
            self._custom_should_intercept = config.SILKY_INTERCEPT_FUNC
        elif config.SILKY_INTERCEPT_PERCENT:
            self._custom_should_intercept = _sample_intercepts
        else:
            self._custom_should_intercept = lambda x: True

    def _should_intercept(self, request):
        """Determine whether or not this request will be intercepted."""
        # First check custom logic.
        if not self._custom_should_intercept(request):
            return False

        # We want to avoid recording any requests/sql queries etc that belong to Silky.
        silky = request.path.startswith(fpath)
        ignored = request.path in config.SILKY_IGNORE_PATHS
        return not (silky or ignored)

    def _apply_dynamic_mappings(self):
        dynamic_profile_configs = config.SILKY_DYNAMIC_PROFILING
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
        if self._should_intercept(request):
            request.silk_is_intercepted = True
            self._apply_dynamic_mappings()
            if not hasattr(SQLCompiler, '_execute_sql'):
                SQLCompiler._execute_sql = SQLCompiler.execute_sql
                SQLCompiler.execute_sql = execute_sql
            request_model = RequestModelFactory(request).construct_request_model()
        DataCollector().configure(request_model)


    def _process_response(self, response):
        with silk_meta_profiler():
            collector = DataCollector()
            collector.stop_python_profiler()
            silk_request = collector.request
            if silk_request:
                silk_response = ResponseModelFactory(response).construct_response_model()
                silk_response.save()
                silk_request.end_time = timezone.now()
                collector.finalise()
                silk_request.save()
            else:
                Logger.error(
                    'No request model was available when processing response. Did something go wrong in process_request/process_view?')


    def process_response(self, request, response):
        if getattr(request, 'silk_is_intercepted', False):
            self._process_response(response)
        return response
