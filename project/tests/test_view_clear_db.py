from django.test import TestCase

from silk import models
from silk.config import SilkyConfig
from silk.middleware import silky_reverse

from .factories import RequestMinFactory


class TestViewClearDB(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        SilkyConfig().SILKY_AUTHENTICATION = False
        SilkyConfig().SILKY_AUTHORISATION = False

    def test_clear_all(self):
        RequestMinFactory.create()
        self.assertEqual(models.Request.objects.count(), 1)
        response = self.client.post(silky_reverse("cleardb"), {"clear_all": "on"})
        self.assertTrue(response.status_code == 200)
        self.assertEqual(models.Request.objects.count(), 0)


class TestViewClearDBAndDeleteProfiles(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        SilkyConfig().SILKY_AUTHENTICATION = False
        SilkyConfig().SILKY_AUTHORISATION = False
        SilkyConfig().SILKY_DELETE_PROFILES = True

    def test_clear_all_and_delete_profiles(self):
        RequestMinFactory.create()
        self.assertEqual(models.Request.objects.count(), 1)
        response = self.client.post(silky_reverse("cleardb"), {"clear_all": "on"})
        self.assertTrue(response.status_code == 200)
        self.assertEqual(models.Request.objects.count(), 0)
