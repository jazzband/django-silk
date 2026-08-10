from unittest.mock import patch

from django.test import TestCase, override_settings
from django.urls import reverse, set_script_prefix

from silk.config import SilkyConfig
from silk.errors import SilkNotConfigured
from silk.middleware import SilkyMiddleware, _should_intercept
from silk.models import Request

from .util import mock_data_collector


def fake_get_response():
    def fake_response():
        return 'hello world'
    return fake_response


class TestApplyDynamicMappings(TestCase):
    def test_dynamic_decorator(self):
        middleware = SilkyMiddleware(fake_get_response)
        SilkyConfig().SILKY_DYNAMIC_PROFILING = [
            {
                'module': 'tests.data.dynamic',
                'function': 'foo'
            }
        ]
        middleware._apply_dynamic_mappings()
        from .data.dynamic import foo

        mock = mock_data_collector()
        with patch('silk.profiling.profiler.DataCollector', return_value=mock) as mock_DataCollector:
            foo()  # Should be wrapped in a decorator
            self.assertTrue(mock_DataCollector.return_value.register_profile.call_count)

    def test_dynamic_context_manager(self):
        middleware = SilkyMiddleware(fake_get_response)
        SilkyConfig().SILKY_DYNAMIC_PROFILING = [
            {
                'module': 'tests.data.dynamic',
                'function': 'foo',
                'start_line': 1,
                'end_line': 2,
            }
        ]
        middleware._apply_dynamic_mappings()
        from .data.dynamic import foo

        mock = mock_data_collector()
        with patch('silk.profiling.profiler.DataCollector', return_value=mock) as mock_DataCollector:
            foo()
            self.assertTrue(mock_DataCollector.return_value.register_profile.call_count)

    def test_invalid_dynamic_context_manager(self):
        middleware = SilkyMiddleware(fake_get_response)
        SilkyConfig().SILKY_DYNAMIC_PROFILING = [
            {
                'module': 'tests.data.dynamic',
                'function': 'foo2',
                'start_line': 1,
                'end_line': 7,
            }
        ]
        self.assertRaises(IndexError, middleware._apply_dynamic_mappings)

    def test_invalid_dynamic_decorator_module(self):
        middleware = SilkyMiddleware(fake_get_response)
        SilkyConfig().SILKY_DYNAMIC_PROFILING = [
            {
                'module': 'tests.data.dfsdf',
                'function': 'foo'
            }
        ]
        self.assertRaises(AttributeError, middleware._apply_dynamic_mappings)

    def test_invalid_dynamic_decorator_function_name(self):
        middleware = SilkyMiddleware(fake_get_response)
        SilkyConfig().SILKY_DYNAMIC_PROFILING = [
            {
                'module': 'tests.data.dynamic',
                'function': 'bar'
            }
        ]
        self.assertRaises(AttributeError, middleware._apply_dynamic_mappings)

    def test_invalid_dynamic_mapping(self):
        middleware = SilkyMiddleware(fake_get_response)
        SilkyConfig().SILKY_DYNAMIC_PROFILING = [
            {
                'dfgdf': 'tests.data.dynamic',
                'funcgdfgtion': 'bar'
            }
        ]
        self.assertRaises(KeyError, middleware._apply_dynamic_mappings)

    def test_no_mappings(self):
        middleware = SilkyMiddleware(fake_get_response)
        SilkyConfig().SILKY_DYNAMIC_PROFILING = [

        ]
        middleware._apply_dynamic_mappings()  # Just checking no crash

    def test_raise_if_authentication_is_enable_but_no_middlewares(self):
        SilkyConfig().SILKY_AUTHENTICATION = True
        with self.modify_settings(MIDDLEWARE={
            'remove': [
                'django.contrib.sessions.middleware.SessionMiddleware',
                'django.contrib.auth.middleware.AuthenticationMiddleware',
                'django.contrib.messages.middleware.MessageMiddleware',
            ],
        }):
            with self.assertRaisesMessage(
                SilkNotConfigured,
                "SILKY_AUTHENTICATION can not be enabled without Session, Authentication or Message Django's middlewares"
            ):
                SilkyMiddleware(fake_get_response)


class TestShouldIntercept(TestCase):
    def test_should_intercept_non_silk_request(self):
        request = Request()
        request.path = '/myapp/foo'
        request.path_info = '/myapp/foo'
        should_intercept = _should_intercept(request)

        self.assertTrue(should_intercept)

    def test_should_intercept_silk_request(self):
        request = Request()
        request.path = reverse('silk:summary')
        request.path_info = reverse('silk:summary')
        should_intercept = _should_intercept(request)

        self.assertFalse(should_intercept)

    @override_settings(ROOT_URLCONF='tests.urlconf_without_silk')
    def test_should_intercept_without_silk_urls(self):
        request = Request()
        request.path = '/login'
        request.path_info = '/login'
        _should_intercept(request)  # Just checking no crash

    def test_should_intercept_ignore_paths(self):
        SilkyConfig().SILKY_IGNORE_PATHS = [
            '/ignorethis'
        ]
        request = Request()
        request.path = '/ignorethis'
        request.path_info = '/ignorethis'
        should_intercept = _should_intercept(request)

        self.assertFalse(should_intercept)

    def test_should_intercept_ignore_paths_behind_script_name_prefix(self):
        """
        Regression test for
        https://github.com/jazzband/django-silk/issues/349

        A SILKY_IGNORE_PATHS entry is a plain string the user writes
        in settings.py -- never passed through reverse() -- so it's
        naturally written without any deployment-specific SCRIPT_NAME
        prefix. Matching it must therefore use path_info (which has
        that prefix stripped), not path (which still has it), or a
        front-end web server prefix causes the entry to go
        unrecognized.
        """
        SilkyConfig().SILKY_IGNORE_PATHS = [
            '/ignorethis'
        ]

        # A path with a SCRIPT_NAME-style prefix that only path_info
        # (not path) has stripped off.
        request = Request()
        request.path = '/some-prefix/ignorethis'
        request.path_info = '/ignorethis'
        should_intercept = _should_intercept(request)

        self.assertFalse(should_intercept)

    def test_should_intercept_silk_request_behind_script_name_prefix(self):
        """
        Companion regression test for
        https://github.com/jazzband/django-silk/issues/349.

        Unlike SILKY_IGNORE_PATHS entries, get_fpath() is built from
        reverse(), which picks up Django's script prefix (set from
        SCRIPT_NAME by the WSGI handler on every real request) just
        like request.path does. So when deployed behind a front-end
        prefix, both request.path and reverse() include it together
        and self-detection must keep comparing against request.path,
        not the prefix-stripped request.path_info.
        """
        set_script_prefix('/some-prefix/')
        try:
            request = Request()
            request.path = reverse('silk:summary')
            request.path_info = reverse('silk:summary')[len('/some-prefix'):]
            should_intercept = _should_intercept(request)

            self.assertFalse(should_intercept)
        finally:
            set_script_prefix('/')
