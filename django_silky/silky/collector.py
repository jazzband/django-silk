class Singleton(type):
    def __init__(cls, name, bases, d):
        super(Singleton, cls).__init__(name, bases, d)
        cls.instance = None

    def __call__(cls, *args):
        if cls.instance is None:
            cls.instance = super(Singleton, cls).__call__(*args)
        return cls.instance


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