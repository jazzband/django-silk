import random
from django.core.urlresolvers import reverse
from django.db.models import Count

from django.test import TestCase
from silk.config import SilkyConfig
from silk import models
from silk.middleware import silky_reverse

from .test_lib.mock_suite import MockSuite


class TestEndPoints(TestCase):
    """
    Hit all the endpoints to check everything actually renders/no error 500s etc.
    Each test will ensure that an object with something to display is chosen to be rendered e.g.
    a request/profile that has queries
    """

    @classmethod
    def setUpClass(cls):
        # We're not testing auth here.
        SilkyConfig().SILKY_AUTHORISATION = False
        SilkyConfig().SILKY_AUTHENTICATION = False
        mock_suite = MockSuite()
        for _ in range(0, 100):
            mock_suite.mock_request()

    def test_summary(self):
        response = self.client.get(silky_reverse('summary'))
        self.assertTrue(response.status_code == 200)

    def test_requests(self):
        response = self.client.get(silky_reverse('requests'))
        self.assertTrue(response.status_code == 200)

    def test_request_detail(self):
        request_id = random.choice(models.Request.objects.all()).pk
        response = self.client.get(silky_reverse('request_detail', kwargs={
            'request_id': request_id
        }))
        self.assertTrue(response.status_code == 200)

    def test_request_sql(self):
        request_id = random.choice(models.SQLQuery.objects.values('request_id').filter(request_id__isnull=False))
        response = self.client.get(silky_reverse('request_sql', kwargs=request_id))
        self.assertTrue(response.status_code == 200)

    def test_request_sql_detail(self):
        fields = {
            'sql_id': 'silk_sqlquery.id',
            'request_id': 'request_id'
        }
        kwargs = random.choice(models.SQLQuery.objects.extra(select=fields).values(*fields.keys()).filter(request_id__isnull=False))
        response = self.client.get(silky_reverse('request_sql_detail', kwargs=kwargs))
        self.assertTrue(response.status_code == 200)

    def test_raw(self):
        request_id = random.choice(models.Request.objects.filter(body__isnull=False)).pk
        url = reverse('silk:raw', kwargs={
            'request_id': request_id
        })+'?typ=request&subtyp=processed'
        response = self.client.get(url)
        code = response.status_code
        self.assertTrue(code == 200)

    def test_request_profiling(self):
        request_id = random.choice(models.Profile.objects.values('request_id').filter(request_id__isnull=False))
        response = self.client.get(silky_reverse('request_profiling', kwargs=request_id))
        self.assertTrue(response.status_code == 200)

    def test_request_profile_detail(self):
        fields = {
            'profile_id': 'silk_profile.id',
            'request_id': 'request_id'
        }
        kwargs = random.choice(models.Profile.objects.extra(select=fields).values(*fields.keys()).filter(request_id__isnull=False))
        response = self.client.get(silky_reverse('request_profile_detail', kwargs=kwargs))
        self.assertTrue(response.status_code == 200)

    def test_request_and_profile_sql(self):
        fields = {
            'profile_id': 'profile_id',
            # 'sql_id': 'sqlquery_id',
            'request_id': 'request_id'
        }
        kwargs = random.choice(models.Profile.objects.extra(select=fields).annotate(num=Count('queries')).values(*fields.keys()).filter(request_id__isnull=False, num__gt=0))
        response = self.client.get(silky_reverse('request_and_profile_sql', kwargs=kwargs))
        self.assertTrue(response.status_code == 200)

    def test_request_and_profile_sql_detail(self):
        fields = {
            'profile_id': 'profile_id',
            'sql_id': 'sqlquery_id',
            'request_id': 'request_id'
        }
        kwargs = random.choice(models.Profile.objects.extra(select=fields).annotate(num=Count('queries')).values(*fields.keys()).filter(request_id__isnull=False, num__gt=0))
        response = self.client.get(silky_reverse('request_and_profile_sql_detail', kwargs=kwargs))
        self.assertTrue(response.status_code == 200)

    def test_profile_detail(self):
        profile_id = random.choice(models.Profile.objects.all()).pk
        response = self.client.get(silky_reverse('profile_detail', kwargs={
            'profile_id': profile_id
        }))
        self.assertTrue(response.status_code == 200)

    def test_profile_sql(self):
        profile_id = random.choice(models.Profile.objects.annotate(num=Count('queries')).values_list('id').filter(num__gt=0))[0]
        response = self.client.get(silky_reverse('profile_sql', kwargs={'profile_id': profile_id}))
        self.assertTrue(response.status_code == 200)

    def test_profile_sql_detail(self):
        profile_id = random.choice(models.Profile.objects.annotate(num=Count('queries')).values_list('id').filter(num__gt=0))[0]
        sql_id = random.choice(models.SQLQuery.objects.filter(profiles=profile_id)).pk
        response = self.client.get(silky_reverse('profile_sql_detail', kwargs={'profile_id': profile_id,
                                                                              'sql_id': sql_id}))
        self.assertTrue(response.status_code == 200)

    def test_profiling(self):
        response = self.client.get(silky_reverse('profiling'))
        self.assertTrue(response.status_code == 200)
