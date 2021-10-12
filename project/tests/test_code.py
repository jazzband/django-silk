from collections import namedtuple

from django.test import TestCase
from silk.views.code import _code, _code_context, _code_context_from_request

FILE_PATH = __file__
LINE_NUM = 5
END_LINE_NUM = 10

with open(__file__) as f:
    ACTUAL_LINES = [l + "\n" for l in f.read().split("\n")]


class CodeTestCase(TestCase):
    def assertActualLineEqual(self, actual_line, end_line_num=None):
        expected_actual_line = ACTUAL_LINES[LINE_NUM - 1 : end_line_num or LINE_NUM]
        self.assertEqual(actual_line, expected_actual_line)

    def assertCodeEqual(self, code):
        expected_code = [
            line.strip("\n") for line in ACTUAL_LINES[0 : LINE_NUM + 10]
        ] + [""]
        self.assertEqual(code, expected_code)

    def test_code(self):
        for end_line_num in None, END_LINE_NUM:
            actual_line, code = _code(FILE_PATH, LINE_NUM, end_line_num)
            self.assertActualLineEqual(actual_line, end_line_num)
            self.assertCodeEqual(code)

    def test_code_context(self):
        for end_line_num in None, END_LINE_NUM:
            for prefix in "", "salchicha_":
                context = _code_context(FILE_PATH, LINE_NUM, end_line_num, prefix)
                self.assertActualLineEqual(
                    context[prefix + "actual_line"], end_line_num
                )
                self.assertCodeEqual(context[prefix + "code"])
                self.assertEqual(context[prefix + "file_path"], FILE_PATH)
                self.assertEqual(context[prefix + "line_num"], LINE_NUM)

    def test_code_context_from_request(self):
        for end_line_num in None, END_LINE_NUM:
            for prefix in "", "salchicha_":
                request = namedtuple("Request", "GET")(
                    dict(file_path=FILE_PATH, line_num=LINE_NUM)
                )
                context = _code_context_from_request(request, end_line_num, prefix)
                self.assertActualLineEqual(
                    context[prefix + "actual_line"], end_line_num
                )
                self.assertCodeEqual(context[prefix + "code"])
                self.assertEqual(context[prefix + "file_path"], FILE_PATH)
                self.assertEqual(context[prefix + "line_num"], LINE_NUM)
