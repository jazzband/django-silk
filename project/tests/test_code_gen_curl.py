import shlex
import textwrap
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
