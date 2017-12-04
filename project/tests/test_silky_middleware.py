try:
    from django.urls import reverse
except ImportError:
    from django.core.urlresolvers import reverse
from django.test import TestCase
from mock import patch, Mock

from silk.config import SilkyConfig
from silk.middleware import SilkyMiddleware, _should_intercept
from silk.models import Request

from .util import mock_data_collector


class TestApplyDynamicMappings(TestCase):
    def test_dynamic_decorator(self):
        middleware = SilkyMiddleware()
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
        middleware = SilkyMiddleware()
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
        middleware = SilkyMiddleware()
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
        middleware = SilkyMiddleware()
        SilkyConfig().SILKY_DYNAMIC_PROFILING = [
            {
                'module': 'tests.data.dfsdf',
                'function': 'foo'
            }
        ]
        self.assertRaises(AttributeError, middleware._apply_dynamic_mappings)

    def test_invalid_dynamic_decorator_function_name(self):
        middleware = SilkyMiddleware()
        SilkyConfig().SILKY_DYNAMIC_PROFILING = [
            {
                'module': 'tests.data.dynamic',
                'function': 'bar'
            }
        ]
        self.assertRaises(AttributeError, middleware._apply_dynamic_mappings)

    def test_invalid_dynamic_mapping(self):
        middleware = SilkyMiddleware()
        SilkyConfig().SILKY_DYNAMIC_PROFILING = [
            {
                'dfgdf': 'tests.data.dynamic',
                'funcgdfgtion': 'bar'
            }
        ]
        self.assertRaises(KeyError, middleware._apply_dynamic_mappings)

    def test_no_mappings(self):
        middleware = SilkyMiddleware()
        SilkyConfig().SILKY_DYNAMIC_PROFILING = [

        ]
        middleware._apply_dynamic_mappings()  # Just checking no crash


class TestShouldIntercept(TestCase):
    def test_should_intercept_non_silk_request(self):
        request = Request()
        request.path = '/myapp/foo'
        should_intercept = _should_intercept(request)

        self.assertTrue(should_intercept)

    def test_should_intercept_silk_request(self):
        request = Request()
        request.path = reverse('silk:summary')
        should_intercept = _should_intercept(request)

        self.assertFalse(should_intercept)

    def test_should_intercept_ignore_paths(self):
        SilkyConfig().SILKY_IGNORE_PATHS = [
            '/ignorethis'
        ]
        request = Request()
        request.path = '/ignorethis'
        should_intercept = _should_intercept(request)

        self.assertFalse(should_intercept)

