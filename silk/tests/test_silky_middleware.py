from django.test import TestCase
from mock import patch, Mock

from silk.config import SilkyConfig
from silk.middleware import SilkyMiddleware


class TestApplyDynamicMappings(TestCase):
    def test_dynamic_decorator(self):
        middleware = SilkyMiddleware()
        SilkyConfig().SILKY_DYNAMIC_PROFILING = [
            {
                'module': 'silk.tests.data.dynamic',
                'function': 'foo'
            }
        ]
        middleware._apply_dynamic_mappings()
        from silk.tests.data.dynamic import foo

        mock = Mock()
        mock.queries = []
        with patch('silk.profiling.profiler.DataCollector', return_value=mock) as mock_DataCollector:
            foo()  # Should be wrapped in a decorator
            self.assertTrue(mock_DataCollector.return_value.register_profile.call_count)

    def test_dynamic_context_manager(self):
        middleware = SilkyMiddleware()
        SilkyConfig().SILKY_DYNAMIC_PROFILING = [
            {
                'module': 'silk.tests.data.dynamic',
                'function': 'foo',
                'start_line': 1,
                'end_line': 2,
            }
        ]
        middleware._apply_dynamic_mappings()
        from silk.tests.data.dynamic import foo

        mock = Mock()
        mock.queries = []
        with patch('silk.profiling.profiler.DataCollector', return_value=mock) as mock_DataCollector:
            foo()
            self.assertTrue(mock_DataCollector.return_value.register_profile.call_count)

    def test_invalid_dynamic_context_manager(self):
        middleware = SilkyMiddleware()
        SilkyConfig().SILKY_DYNAMIC_PROFILING = [
            {
                'module': 'silk.tests.data.dynamic',
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
                'module': 'silk.tests.data.dfsdf',
                'function': 'foo'
            }
        ]
        self.assertRaises(AttributeError, middleware._apply_dynamic_mappings)

    def test_invalid_dynamic_decorator_function_name(self):
        middleware = SilkyMiddleware()
        SilkyConfig().SILKY_DYNAMIC_PROFILING = [
            {
                'module': 'silk.tests.data.dynamic',
                'function': 'bar'
            }
        ]
        self.assertRaises(AttributeError, middleware._apply_dynamic_mappings)

    def test_invalid_dynamic_mapping(self):
        middleware = SilkyMiddleware()
        SilkyConfig().SILKY_DYNAMIC_PROFILING = [
            {
                'dfgdf': 'silk.tests.data.dynamic',
                'funcgdfgtion': 'bar'
            }
        ]
        self.assertRaises(KeyError, middleware._apply_dynamic_mappings)

    def test_no_mappings(self):
        middleware = SilkyMiddleware()
        SilkyConfig().SILKY_DYNAMIC_PROFILING = [

        ]
        middleware._apply_dynamic_mappings()  # Just checking no crash

