from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("django-silk")
except PackageNotFoundError:
    __version__ = "unknown"
