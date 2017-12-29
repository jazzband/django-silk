from django.contrib.auth.models import User
try:
    # Django >= 1.10
    from django.urls import reverse, NoReverseMatch
except ImportError:
    # Django < 2.0
    from django.core.urlresolvers import reverse, NoReverseMatch
from django.test import TestCase

from silk.config import SilkyConfig, default_permissions
from silk.middleware import silky_reverse


class TestAuth(TestCase):
    def test_authentication(self):
        SilkyConfig().SILKY_AUTHENTICATION = True
        response = self.client.get(silky_reverse('requests'))
        self.assertEqual(response.status_code, 302)
        url = response.url
        try:
            # If we run tests within the django_silk project, a login url is available from example_app
            self.assertIn(reverse('login'), url)
        except NoReverseMatch:
            # Otherwise the Django default login url is used, in which case we can test for that instead
            self.assertIn('http://testserver/login/', url)

    def test_default_authorisation(self):
        SilkyConfig().SILKY_AUTHENTICATION = True
        SilkyConfig().SILKY_AUTHORISATION = True
        SilkyConfig().SILKY_PERMISSIONS = default_permissions
        username_and_password = 'bob'  # bob is an imbecile and uses the same pass as his username
        user = User.objects.create(username=username_and_password)
        user.set_password(username_and_password)
        user.save()
        self.client.login(username=username_and_password, password=username_and_password)
        response = self.client.get(silky_reverse('requests'))
        self.assertEqual(response.status_code, 403)
        user.is_staff = True
        user.save()
        response = self.client.get(silky_reverse('requests'))
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
        response = self.client.get(silky_reverse('requests'))
        self.assertEqual(response.status_code, 403)
        user.username = 'mike2'
        user.save()
        response = self.client.get(silky_reverse('requests'))
        self.assertEqual(response.status_code, 200)

