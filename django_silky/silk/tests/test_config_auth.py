from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase

from silk.config import SilkyConfig, default_permissions


__author__ = 'mtford'


class TestAuth(TestCase):


    def test_authentication(self):
        SilkyConfig().SILKY_AUTHENTICATION = True
        response = self.client.get(reverse('silk:requests'))
        self.assertEqual(response.status_code, 302)
        try:
            url = response.url
        except AttributeError:  # Django 1.5
            url = response['location']
        self.assertIn(reverse('login'), url)


    def test_default_authorisation(self):
        SilkyConfig().SILKY_AUTHENTICATION = True
        SilkyConfig().SILKY_AUTHORISATION = True
        SilkyConfig().SILKY_PERMISSIONS = default_permissions
        username_and_password = 'bob'  # bob is an imbecile and uses the same pass as his username
        user = User.objects.create(username=username_and_password)
        user.set_password(username_and_password)
        user.save()
        self.client.login(username=username_and_password, password=username_and_password)
        response = self.client.get(reverse('silk:requests'))
        self.assertEqual(response.status_code, 403)
        user.is_staff = True
        user.save()
        response = self.client.get(reverse('silk:requests'))
        self.assertEqual(response.status_code, 200)


    def test_custom_authorisation(self):
        SilkyConfig().SILKY_AUTHENTICATION = True
        SilkyConfig().SILKY_AUTHORISATION = True
        def custom_authorisation(user):
            return user.username.startswith('mike')

        SilkyConfig().SILKY_PERMISSIONS = custom_authorisation
        username_and_password = 'bob'  # bob is an imbecile and uses the same pass as his username
        user = User.objects.create(username=username_and_password)
        user.set_password(username_and_password)
        user.save()
        self.client.login(username=username_and_password, password=username_and_password)
        response = self.client.get(reverse('silk:requests'))
        self.assertEqual(response.status_code, 403)
        user.username = 'mike2'
        user.save()
        response = self.client.get(reverse('silk:requests'))
        self.assertEqual(response.status_code, 200)

