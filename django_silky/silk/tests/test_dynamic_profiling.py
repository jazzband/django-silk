from django.test import TestCase
from mock import patch
import six
import silk
from silk.profiling.dynamic import _get_module, _get_parent_module, profile_function_or_method


class TestGetModule(TestCase):
    """test for _get_module"""

    def test_singular(self):
        module = _get_module('silk')
        self.assertEqual(module.__class__.__name__, 'module')
        self.assertEqual('silk', module.__name__)
        self.assertTrue(hasattr(module, 'models'))

    def test_dot(self):
        module = _get_module('silk.models')
        self.assertEqual(module.__class__.__name__, 'module')
        self.assertEqual('silk.models', module.__name__)
        self.assertTrue(hasattr(module, 'SQLQuery'))


class TestGetParentModule(TestCase):
    """test for silk.tools._get_parent_module"""

    def test_singular(self):
        parent = _get_parent_module(silk)
        self.assertIsInstance(parent, dict)

    def test_dot(self):
        import silk.utils

        parent = _get_parent_module(silk.utils)
        self.assertEqual(parent, silk)


class MyClass(object):
    def foo(self):
        pass


def foo():
    pass


def source_file_name():
    file_name = __file__
    if file_name[-1] == 'c':
        file_name = file_name[:-1]
    return file_name


class TestProfileFunction(TestCase):
    def test_method_as_str(self):
        # noinspection PyShadowingNames
        def foo(_):
            pass

        # noinspection PyUnresolvedReferences
        with patch.object(MyClass, 'foo', foo):
            profile_function_or_method('silk.tests.test_dynamic_profiling', 'MyClass.foo', 'test')
            with patch('silk.profiling.profiler.Profile') as mock_Profile:
                MyClass().foo()
                # noinspection PyUnresolvedReferences
                mock_Profile.assert_called_once_with(func_name=foo.__name__,
                                                     dynamic=True,
                                                     file_path=source_file_name(),
                                                     name='test',
                                                     line_num=six.get_function_code(foo).co_firstlineno)

    def test_func_as_str(self):
        name = foo.__name__
        line_num = six.get_function_code(foo).co_firstlineno
        profile_function_or_method('silk.tests.test_dynamic_profiling', 'foo', 'test')
        with patch('silk.profiling.profiler.Profile') as mock_Profile:
            foo()
            # noinspection PyUnresolvedReferences
            mock_Profile.assert_called_once_with(func_name=name,
                                                 dynamic=True,
                                                 file_path=source_file_name(),
                                                 name='test',
                                                 line_num=line_num)