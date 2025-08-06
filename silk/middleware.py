import logging
import random

from django.conf import settings
from django.db import DatabaseError, router, transaction
from django.db.models.sql.compiler import SQLCompiler
from django.urls import NoReverseMatch, reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from silk import models
from silk.collector import DataCollector
from silk.config import SilkyConfig
from silk.errors import SilkNotConfigured
from silk.model_factory import RequestModelFactory, ResponseModelFactory
from silk.profiling import dynamic
from silk.profiling.profiler import silk_meta_profiler
from silk.sql import execute_sql

Logger = logging.getLogger('silk.middleware')


def silky_reverse(name, *args, **kwargs):
    try:
        r = reverse('silk:%s' % name, *args, **kwargs)
    except NoReverseMatch:
        # In case user forgets to set namespace, but also fixes Django 1.5 tests on Travis
        # Hopefully if user has forgotten to add namespace there are no clashes with their own
        # view names but I don't think there is really anything can do about this.
        r = reverse(name, *args, **kwargs)
    return r


def get_fpath():
    return silky_reverse('summary')


config = SilkyConfig()
AUTH_AND_SESSION_MIDDLEWARES = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]


def _should_intercept(request):
    """we want to avoid recording any requests/sql queries etc that belong to Silky"""
    # Check custom intercept logic.
    if config.SILKY_INTERCEPT_FUNC:
        if not config.SILKY_INTERCEPT_FUNC(request):
            return False
    # don't trap every request
    elif config.SILKY_INTERCEPT_PERCENT < 100:
        if random.random() > config.SILKY_INTERCEPT_PERCENT / 100.0:
            return False

    try:
        silky = request.path.startswith(get_fpath())
    except NoReverseMatch:
        silky = False

    ignored = request.path in config.SILKY_IGNORE_PATHS
    return not (silky or ignored)


class TestMiddleware:
    def process_response(self, request, response):
        return response

    def process_request(self, request):
        return


class SilkyMiddleware:
    def __init__(self, get_response):
        if config.SILKY_AUTHENTICATION and not (
            set(AUTH_AND_SESSION_MIDDLEWARES) & set(settings.MIDDLEWARE)
        ):
            raise SilkNotConfigured(
                _("SILKY_AUTHENTICATION can not be enabled without Session, "
                  "Authentication or Message Django's middlewares")
            )

        self.get_response = get_response

    def __call__(self, request):
        self.process_request(request)

        # To be able to persist filters when Session and Authentication
        # middlewares are not present.
        # Unlike session (which stores in DB) it won't persist filters
        # after refresh the page.
        request.silk_filters = {}

        response = self.get_response(request)

        response = self.process_response(request, response)

        return response

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
        DataCollector().clear()

        if not _should_intercept(request):
            return

        Logger.debug('process_request')
        request.silk_is_intercepted = True
        self._apply_dynamic_mappings()
        if not hasattr(SQLCompiler, '_execute_sql'):
            SQLCompiler._execute_sql = SQLCompiler.execute_sql
            SQLCompiler.execute_sql = execute_sql

        silky_config = SilkyConfig()

        should_profile = silky_config.SILKY_PYTHON_PROFILER
        if silky_config.SILKY_PYTHON_PROFILER_FUNC:
            should_profile = silky_config.SILKY_PYTHON_PROFILER_FUNC(request)

        request_model = RequestModelFactory(request).construct_request_model()
        DataCollector().configure(request_model, should_profile=should_profile)

    def _process_response(self, request, response):
        Logger.debug('Process response')
        with transaction.atomic(using=router.db_for_write(models.SQLQuery)):
            with silk_meta_profiler():
                collector = DataCollector()
                collector.stop_python_profiler()
                silk_request = collector.request
                if silk_request:
                    ResponseModelFactory(response).construct_response_model()
                    silk_request.end_time = timezone.now()
                    collector.finalise()
                else:
                    Logger.error(
                        'No request model was available when processing response. '
                        'Did something go wrong in process_request/process_view?'
                        '\n' + str(request) + '\n\n' + str(response)
                    )
            # Need to save the data outside the silk_meta_profiler
            # Otherwise the  meta time collected in the context manager
            # is not taken in account
            if silk_request:
                silk_request.save()

        Logger.debug('Process response done.')

    def process_response(self, request, response):
        max_attempts = 2
        attempts = 1
        if getattr(request, 'silk_is_intercepted', False):
            while attempts <= max_attempts:
                if attempts > 1:
                    Logger.debug('Retrying _process_response; attempt %s' % attempts)
                try:
                    self._process_response(request, response)
                    break
                except (AttributeError, DatabaseError):
                    if attempts >= max_attempts:
                        Logger.warning('Exhausted _process_response attempts; not processing request')
                        break
                attempts += 1
        return response
