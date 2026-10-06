from django.core import management
from django.test import TestCase
from django.utils import timezone

from silk import models

from .factories import RequestMinFactory, ResponseFactory, SQLQueryFactory


class TestClearRequestLogCommand(TestCase):
    def test_clears_completed_requests(self):
        completed = RequestMinFactory.create(end_time=timezone.now())
        ResponseFactory.create(request=completed)
        SQLQueryFactory.create(request=completed)

        management.call_command("silk_clear_request_log")

        self.assertEqual(models.Request.objects.count(), 0)
        self.assertEqual(models.Response.objects.count(), 0)
        self.assertEqual(models.SQLQuery.objects.count(), 0)

    def test_preserves_in_flight_requests(self):
        completed = RequestMinFactory.create(end_time=timezone.now())
        ResponseFactory.create(request=completed)
        in_flight = RequestMinFactory.create()
        SQLQueryFactory.create(request=in_flight)

        management.call_command("silk_clear_request_log")

        self.assertFalse(models.Request.objects.filter(pk=completed.pk).exists())
        self.assertTrue(models.Request.objects.filter(pk=in_flight.pk).exists())
        self.assertEqual(models.SQLQuery.objects.filter(request=in_flight).count(), 1)
