from unittest import TestCase

from mock import patch

import silky
from silky.tools import _get_module, _get_parent_module, \
    inject_context_manager_module, _inject_context_manager_func, inject_context_manager_func, \
    profile_function_or_method


def wtf():
    pass


class MyClass(object):
    def foo(self):
        pass


class TestGetModule(TestCase):
    """test for _get_module"""

    def test_singular(self):
        module = _get_module('silky')
        self.assertEqual(module.__class__.__name__, 'module')
        self.assertEqual('silky', module.__name__)
        self.assertTrue(hasattr(module, 'models'))

    def test_dot(self):
        module = _get_module('silky.models')
        self.assertEqual(module.__class__.__name__, 'module')
        self.assertEqual('silky.models', module.__name__)
        self.assertTrue(hasattr(module, 'SQLQuery'))


class TestGetParentModule(TestCase):
    """test for silky.tools._get_parent_module"""

    def test_singular(self):
        parent = _get_parent_module(silky)
        self.assertIsInstance(parent, dict)

    def test_dot(self):
        parent = _get_parent_module(silky.tools)
        self.assertEqual(parent, silky)


class TestInject(TestCase):
    def test_inject_context_manager_module(self):
        with patch('silky.profiler.silky_profile') as silky_profile:
            new_module = inject_context_manager_module('silky.tests.data.dynamic', 5, 7, 'test')
            new_module.foo()
            silky_profile.assert_called_once_with('test')

    def test_inject_context_manager_func_raw(self):
        x = 5

        def foo():
            print x
            v = 99
            print v
            print '1'
            print '2'
            print '3'

        bar = _inject_context_manager_func(foo, 0, 2, 'test')
        with patch('silky.profiler.silky_profile') as silky_profile:
            foo()
            self.assertFalse(silky_profile.call_count)
        with patch('silky.profiler.silky_profile') as silky_profile:
            bar()
            silky_profile.assert_called_once_with('test')


    def test_inject_context_manager_func(self):
        global foo

        def bar():
            v = 2
            print v
            print '1'
            print '2'
            print '3'

        foo = bar
        inject_context_manager_func('silky.tests.test_dynamic_profiling', 'foo', 0, 2, 'test')
        with patch('silky.profiler.silky_profile') as silky_profile:
            foo()
            silky_profile.assert_called_once_with('test')


class TestProfileFunction(TestCase):
    def test_method(self):
        with patch.object(MyClass, 'foo') as wrapped_foo:
            with patch('silky.tools.silky_profile') as silky_profile:
                profile_function_or_method('silky.tests.test_dynamic_profiling', 'MyClass.foo', 'test')
                silky_profile.assert_called_once_with('test')
                __call__ = silky_profile.return_value
                __call__.assert_called_once_with(wrapped_foo)

    def test_func(self):
        blah = foo
        with patch('silky.tools.silky_profile') as silky_profile:
            profile_function_or_method('silky.tests.test_dynamic_profiling', 'foo', 'test')
            silky_profile.assert_called_once_with('test')
            __call__ = silky_profile.return_value
            __call__.assert_called_once_with(blah)