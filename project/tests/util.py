import io
from unittest.mock import Mock

from django.core.files import File
from django.core.files.storage import Storage

from silk.models import Request


def mock_data_collector():
    mock = Mock()
    mock.queries = []
    mock.local = Mock()
    r = Request()
    mock.local.request = r
    mock.request = r
    return mock


def delete_all_models(model_class):
    """
    A sqlite3-safe deletion function to avoid "django.db.utils.OperationalError: too many SQL variables"
    :param model_class:
    :return:
    """
    while model_class.objects.count():
        ids = model_class.objects.values_list('pk', flat=True)[:80]
        model_class.objects.filter(pk__in=ids).delete()


class DictStorage(Storage):
    """Storage that stores files in a dictionary - for testing."""

    def __init__(self):
        self.files = {}

    def open(self, name, mode="rb"):
        if name not in self.files:
            self.files[name] = b""
        return File(io.BytesIO(self.files[name]), name=name)

    def get_valid_name(self, name):
        return name

    def exists(self, name):
        return name in self.files
