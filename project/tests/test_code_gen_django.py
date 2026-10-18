from unittest import TestCase

from silk.code_generation.django_test_client import gen


class TestCodeGenDjango(TestCase):
    def test_post(self):
        result = gen(
            path="/alpha/beta",
            method="POST",
            data={"gamma": "delta", "epsilon": "zeta"},
            content_type="application/x-www-form-urlencoded",
        )

        self.assertIn("from django.test import Client", result)
        self.assertIn("c = Client()", result)
        self.assertIn("c.post(path='/alpha/beta'", result)
        self.assertIn("content_type='application/x-www-form-urlencoded')", result)
