from silky.singleton import Singleton


class DataCollector(object):
    __metaclass__ = Singleton

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
        map(self.queries.append, args)