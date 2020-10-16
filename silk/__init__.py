from pkg_resources import get_distribution, DistributionNotFound

try:
    __version__ = get_distribution("django-silk").version
except DistributionNotFound:
    pass
