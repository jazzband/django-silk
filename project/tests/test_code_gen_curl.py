import shlex
from unittest import TestCase

from silk.code_generation.curl import curl_cmd


class TestCodeGenCurl(TestCase):
    def test_post_json(self):
        result = curl_cmd(
            url="https://example.org/alpha/beta",
            method="POST",
            body={"gamma": "delta"},
            content_type="application/json",
        )

        result_words = shlex.split(result)

        self.assertEqual(result_words, [
            'curl', '-X', 'POST',
            '-H', 'content-type: application/json',
            '-d', '{"gamma": "delta"}',
            'https://example.org/alpha/beta'
        ])

    def test_non_string_query_param_value(self):
        """
        Regression test for
        https://github.com/jazzband/django-silk/issues/317

        A non-string query param value (e.g. a float, as in the
        issue's reproduction) must not raise AttributeError when
        generating the curl command.
        """
        result = curl_cmd(
            url="https://example.org/alpha/beta",
            method="GET",
            query_params={"log_time": 1543406262.021423},
            content_type="application/json",
        )

        self.assertIn("log_time=1543406262.021423", result)
