# future
from __future__ import print_function
# std
import cProfile
# 3rd party
import contextlib2 as contextlib
from six import StringIO
from django.test import TestCase
# silk
from silk.utils.profile_parser import parse_profile


class ProfileParserTestCase(TestCase):

    def test_profile_parser(self):
        """
        Verify that the function parse_profile produces the expected output.
        """
        with contextlib.closing(StringIO()) as stream:
            with contextlib.redirect_stdout(stream):
                cProfile.run('print()')
            stream.seek(0)
            actual = list(parse_profile(stream))
            expected = [
                 ['ncalls', 'tottime', 'percall', 'cumtime', 'percall', 'filename:lineno(function)'],
                 ['1', '0.000', '0.000', '0.000', '0.000', '<string>:1(<module>)'],
                 ['1', '0.000', '0.000', '0.000', '0.000', '{built-in method builtins.exec}'],
                 ['1', '0.000', '0.000', '0.000', '0.000', '{built-in method builtins.print}'],
                 ['1', '0.000', '0.000', '0.000', '0.000', "{method 'disable' of '_lsprof.Profiler' objects}"],
            ]
            self.assertListEqual(actual, expected)