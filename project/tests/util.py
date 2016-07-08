from mock import Mock
from silk.models import Request


def mock_data_collector():
    mock = Mock()
    mock.queries = []
    mock.local = Mock()
    r = Request()
    mock.local.request = r
    mock.request = r
    return mock
