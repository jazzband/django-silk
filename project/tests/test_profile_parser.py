# future
from __future__ import print_function
# std
import cProfile
# 3rd party
import contextlib2 as contextlib
from six import StringIO, PY3
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
            if PY3:
                expected = [
                     ['ncalls', 'tottime', 'percall', 'cumtime', 'percall', 'filename:lineno(function)'],
                     ['1', '0.000', '0.000', '0.000', '0.000', '<string>:1(<module>)'],
                     ['1', '0.000', '0.000', '0.000', '0.000', '{built-in method builtins.exec}'],
                     ['1', '0.000', '0.000', '0.000', '0.000', '{built-in method builtins.print}'],
                     ['1', '0.000', '0.000', '0.000', '0.000', "{method 'disable' of '_lsprof.Profiler' objects}"],
                ]
            else:
                expected = [
                    ['ncalls', 'tottime', 'percall', 'cumtime', 'percall', 'filename:lineno(function)'],
                    ['1', '0.000', '0.000', '0.000', '0.000', '<string>:1(<module>)'],
                    ['2', '0.000', '0.000', '0.000', '0.000', 'StringIO.py:208(write)'],
                    ['2', '0.000', '0.000', '0.000', '0.000', 'StringIO.py:38(_complain_ifclosed)'],
                    ['2', '0.000', '0.000', '0.000', '0.000', '{isinstance}'],
                    ['2', '0.000', '0.000', '0.000', '0.000', '{len}'],
                    ['2', '0.000', '0.000', '0.000', '0.000', "{method 'append' of 'list' objects}"],
                    ['1', '0.000', '0.000', '0.000', '0.000', "{method 'disable' of '_lsprof.Profiler' objects}"]
                ]

            self.assertListEqual(actual, expected)