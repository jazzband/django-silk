from django.test import TestCase
from mock import patch

from silky.config import SilkyConfig
from silky.middleware import SilkyMiddleware


class TestApplyDynamicMappings(TestCase):
    def test_dynamic_decorator(self):
        middleware = SilkyMiddleware()
        SilkyConfig().SILKY_DYNAMIC_PROFILING = [
            {
                'module': 'silky.tests.data.dynamic',
                'function': 'foo'
            }
        ]
        middleware._apply_dynamic_mappings()
        from silky.tests.data.dynamic import foo

        with patch('silky.profiling.profiler.Profile') as mock_Profile:
            foo()  # Should be wrapped in a decorator
            self.assertTrue(mock_Profile.call_count)

    def test_dynamic_context_manager(self):
        middleware = SilkyMiddleware()
        SilkyConfig().SILKY_DYNAMIC_PROFILING = [
            {
                'module': 'silky.tests.data.dynamic',
                'function': 'foo',
                'start_line': 1,
                'end_line': 2,
            }
        ]
        middleware._apply_dynamic_mappings()
        from silky.tests.data.dynamic import foo

        with patch('silky.profiling.profiler.Profile') as mock_Profile:
            foo()  # Should be wrapped in a decorator
            self.assertTrue(mock_Profile.call_count)

    def test_invalid_dynamic_context_manager(self):
        middleware = SilkyMiddleware()
        SilkyConfig().SILKY_DYNAMIC_PROFILING = [
            {
                'module': 'silky.tests.data.dynamic',
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
                'module': 'silky.tests.data.dfsdf',
                'function': 'foo'
            }
        ]
        self.assertRaises(AttributeError, middleware._apply_dynamic_mappings)

    def test_invalid_dynamic_decorator_function_name(self):
        middleware = SilkyMiddleware()
        SilkyConfig().SILKY_DYNAMIC_PROFILING = [
            {
                'module': 'silky.tests.data.dynamic',
                'function': 'bar'
            }
        ]
        self.assertRaises(AttributeError, middleware._apply_dynamic_mappings)

    def test_invalid_dynamic_mapping(self):
        middleware = SilkyMiddleware()
        SilkyConfig().SILKY_DYNAMIC_PROFILING = [
            {
                'dfgdf': 'silky.tests.data.dynamic',
                'funcgdfgtion': 'bar'
            }
        ]
        self.assertRaises(KeyError, middleware._apply_dynamic_mappings)

    def test_no_mappings(self):
        middleware = SilkyMiddleware()
        SilkyConfig().SILKY_DYNAMIC_PROFILING = [

        ]
        middleware._apply_dynamic_mappings()  # Just checking no crash

