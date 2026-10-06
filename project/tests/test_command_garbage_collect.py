from django.core import management
from django.test import TestCase
from django.utils import timezone

from silk import models
from silk.config import SilkyConfig

from .factories import RequestMinFactory


class TestGarbageCollectCommand(TestCase):
    def test_garbage_collect_command(self):
        SilkyConfig().SILKY_MAX_RECORDED_REQUESTS = 2
        now = timezone.now()
        for _ in range(3):
            RequestMinFactory.create(end_time=now)
        self.assertEqual(models.Request.objects.count(), 3)
        management.call_command("silk_request_garbage_collect")
        self.assertEqual(models.Request.objects.count(), 2)
        management.call_command("silk_request_garbage_collect", max_requests=1)
        self.assertEqual(models.Request.objects.count(), 1)
        management.call_command(
            "silk_request_garbage_collect", max_requests=0, verbosity=2
        )
        self.assertEqual(models.Request.objects.count(), 0)
