from threading import local

from six import with_metaclass
from silk import models
from silk.models import SQLQuery

from silk.singleton import Singleton


class DataCollector(with_metaclass(Singleton, object)):
    """
    Provides the ability to save all models at the end of the request. We cannot save during
    the request due to the possibility of atomic blocks and hence must collect data and perform
    the save at the end.
    """
    def __init__(self):
        super(DataCollector, self).__init__()
        self.local = local()
        self._configure()

    @property
    def request(self):
        return getattr(self.local, 'request', None)

    def get_identifier(self):
        self.local.temp_identifier += 1
        return self.local.temp_identifier

    @request.setter
    def request(self, value):
        self.local.request = value

    @property
    def queries(self):
        queries = getattr(self.local, 'queries', {})
        return queries.values()

    @queries.setter
    def queries(self, value):
        self.local.queries = value

    @property
    def profiles(self):
        profiles = getattr(self.local, 'profiles', {})
        return profiles.values()

    def query_with_temp_id(self, ident):
        return self.local.queries.get(ident, None)

    def profile_with_temp_id(self, ident):
        return self.local.profiles.get(ident, None)

    @profiles.setter
    def profiles(self, value):
        self.local.profiles = value

    def _configure(self):
        self.queries = {}
        self.profiles = {}
        self.local.temp_identifier = 0

    def configure(self, request=None):
        self.request = request
        self._configure()

    def clear(self):
        self.request = None
        self._configure()

    def register_query(self, *args):
        for arg in args:
            ident = self.get_identifier()
            arg['temp_id'] = ident
            self.local.queries[ident] = arg

    def register_profile(self, *args):
        for arg in args:
            ident = self.get_identifier()
            arg['temp_id'] = ident
            self.local.profiles[ident] = arg

    def finalise(self):
        for query in self.queries:
            del(query['temp_id'])
            query_model = models.SQLQuery.objects.create(**query)
            query['pk'] = query_model.pk
        for profile in self.profiles:
            del(profile['temp_id'])
            pks = [x['pk'] for x in profile['queries']]
            del(profile['queries'])
            profile = models.Profile.objects.create(**profile)
            queries = SQLQuery.objects.filter(pk__in=pks)
            profile.queries = queries
            profile.save()