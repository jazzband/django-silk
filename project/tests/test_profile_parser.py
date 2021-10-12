import cProfile
import io
import re

import contextlib2 as contextlib
from django.test import TestCase

from silk.utils.profile_parser import parse_profile


class ProfileParserTestCase(TestCase):
    def test_profile_parser(self):
        """
        Verify that the function parse_profile produces the expected output.
        """
        with contextlib.closing(io.StringIO()) as stream:
            with contextlib.redirect_stdout(stream):
                cProfile.run('print()')
            stream.seek(0)
            actual = list(parse_profile(stream))

            # Expected format for the profiling output on cPython implementations (PyPy differs)
            # actual = [
            #     ["ncalls", "tottime", "percall", "cumtime", "percall", "filename:lineno(function)"],
            #     ["1", "0.000", "0.000", "0.000", "0.000", "<string>:1(<module>)"],
            #     ["1", "0.000", "0.000", "0.000", "0.000", "{built-in method builtins.exec}"],
            #     ["1", "0.000", "0.000", "0.000", "0.000", "{built-in method builtins.print}"],
            #     ["1", "0.000", "0.000", "0.000", "0.000", "{method 'disable' of '_lsprof.Profiler' objects}"],
            # ]

            exc_header = ["ncalls", "tottime", "percall", "cumtime", "percall", "filename:lineno(function)"]
            self.assertEqual(actual[0], exc_header)

            exc_number = re.compile(r"\d(.\d+)?")
            exc_module = re.compile(r"({method.*})|({built-in.*})|(<.+>:\d+\(<.+>\))")

            exc_row = [exc_number, exc_number, exc_number, exc_number, exc_number, exc_module]

            for row in actual[1:]:
                for text, expected_regex in zip(row, exc_row):
                    self.assertRegex(
                        text, expected_regex,
                        msg="Expected something like {} but found {}"
                    )
