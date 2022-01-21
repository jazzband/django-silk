from django.core import management
from django.test import TestCase

from silk import models
from silk.config import SilkyConfig

from .factories import RequestMinFactory


class TestViewClearDB(TestCase):
    def test_garbage_collect_command(self):
        SilkyConfig().SILKY_MAX_RECORDED_REQUESTS = 2
        RequestMinFactory.create_batch(3)
        self.assertEqual(models.Request.objects.count(), 3)
        management.call_command("silk_request_garbage_collect")
        self.assertEqual(models.Request.objects.count(), 2)
        management.call_command("silk_request_garbage_collect", max_requests=1)
        self.assertEqual(models.Request.objects.count(), 1)
        management.call_command("silk_request_garbage_collect", max_requests=0)
        self.assertEqual(models.Request.objects.count(), 0)
