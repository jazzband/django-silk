from threading import local

from six import with_metaclass

from silky.singleton import Singleton


class DataCollector(with_metaclass(Singleton, object)):
    def __init__(self):
        super(DataCollector, self).__init__()
        self.local = local()

    @property
    def request(self):
        return getattr(self.local, 'request', None)

    @request.setter
    def request(self, value):
        self.local.request = value

    @property
    def queries(self):
        return getattr(self.local, 'queries', None)

    @queries.setter
    def queries(self, value):
        self.local.queries = value

    def configure(self, request):
        self.request = request
        self.queries = []

    def clear(self):
        self.request = None
        self.queries = []

    def register_query(self, *args):
        for arg in args:
            self.queries.append(arg)