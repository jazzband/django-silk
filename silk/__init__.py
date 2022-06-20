import django
from pkg_resources import DistributionNotFound, get_distribution

try:
    __version__ = get_distribution("django-silk").version
except DistributionNotFound:
    pass

if django.VERSION < (3, 2):
    default_app_config = "silk.apps.SilkAppConfig"
