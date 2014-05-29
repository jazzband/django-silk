from six import with_metaclass
from silky.singleton import Singleton


class DataCollector(with_metaclass(Singleton, object)):

    def __init__(self):
        super(DataCollector, self).__init__()
        self.request = None
        self.queries = []

    def configure(self, request):
        self.request = request

    def clear(self):
        self.request = None
        self.queries = []

    def register_query(self, *args):
        for arg in args:
            self.queries.append(arg)