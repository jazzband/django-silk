import logging

from silky import models


current_request_key = 'current_request'
profiles_key = 'profiles'
queries_key = 'queries'

Logger = logging.getLogger('silky')


class Singleton(type):
    def __init__(cls, name, bases, d):
        super(Singleton, cls).__init__(name, bases, d)
        cls.instance = None

    def __call__(cls, *args):
        if cls.instance is None:
            cls.instance = super(Singleton, cls).__call__(*args)
        return cls.instance


class DataCollector(object):
    """
    Provides the ability to save everything in bulk at the end of a request to have as
    little impact on response time as possible.
    """
    __metaclass__ = Singleton

    def __init__(self):
        super(DataCollector, self).__init__()
        self.request = None
        self.request_queries = None
        self.profile_queries = None

    def configure(self, request):
        self.request = request
        self.request_queries = []
        self.profile_queries = []

    def register_query(self, query):
        self.request_queries.append(query)

    def register_queries_for_profile(self, profile, queries):
        self.profile_queries.append((profile, queries))

    def save(self):
        assert self.request, 'no request was registered'
        self.request.save()
        # Annoyingly we cant bulk_create either the profiles or the queries as we need the pks for use in ManyToMany.
        # There is a ticket for this though: https://code.djangoproject.com/ticket/19527.
        # Looks like some progress is being made on it, however Oracle DB is holding it back.
        # This is pretty shit though as if we have 1000 sql queries that we've captured we then have to make 1000 sql
        # queries ourselves which means silky has a massive impact on response time...
        for query in self.request_queries:
            query.request = self.request
            query.save()
        for profile, queries in self.profile_queries:
            profile.request = self.request
            profile.save()
            profile.queries.add(*queries)
            profile.save()
        for query in self.request_queries:
            query.save()

