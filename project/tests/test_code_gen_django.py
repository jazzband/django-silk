import textwrap
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

        self.assertEqual(result, textwrap.dedent("""\
            from django.test import Client
            c = Client()
            response = c.post(path='/alpha/beta',
                              data={'gamma': 'delta', 'epsilon': 'zeta'},
                              content_type='application/x-www-form-urlencoded')
        """))
