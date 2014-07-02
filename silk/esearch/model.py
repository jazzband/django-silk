"""
Provision serialisation of django models/dictionaries to Elasticsearch.

It's rather inefficient at the moment in that relations are nested JSON. This is fine
in that we never actually modify anything after the fact and so it's time efficient.
What it gains in time, we lose in space efficiency however.
"""
import collections

from django.db.models import ForeignKey, ManyToManyField, OneToOneField, DateTimeField, Field
from django.db.models.fields.related import ForeignRelatedObjectsDescriptor
import rawes
import six

from silk.config import SilkyConfig


class ExtraField():
    def __init__(self, source=None):
        self.source = source


class ESIndexerMeta(type):
    def __init__(cls, name, bases, dct):
        super(ESIndexerMeta, cls).__init__(name, bases, dct)

    def __new__(mcs, name, bases, dct):
        inst = super(ESIndexerMeta, mcs).__new__(mcs, name, bases, dct)
        opts = {
            'extra_fields': []
        }
        for k, v in inst.__dict__.items():
            if isinstance(v, ExtraField):
                opts['extra_fields'].append(v.source or k)
                delattr(inst, k)
        setattr(inst, '_opts', opts)
        return inst


class ESIndexer(six.with_metaclass(ESIndexerMeta, object)):
    """
    Takes a Django model or dictionary and creates a serialised object
    to send to Elasticsearch.

    If given a dictionary, a model_class must be supplied to act as a 'specification'.
    This means we use the same Schema when using both the configured Django database
    and Elasticsearch.

    Models are serialised along with serialised relationships and reverse relationships to a depth of 1
    """
    model_class = None
    index = None
    es_type = None

    POST = '/{index}/{type}/'

    def __init__(self, model, follow_reverse=True):
        """
        :param model: a dictionary or an object, doesn't matter.
        :param follow_reverse: specifies whether or not should serialise reverse relationships.
        """
        super(ESIndexer, self).__init__()
        self.model = model
        self.follow_reverse = follow_reverse

    def _dir_map(self, model):
        """
        :param model:
        :return: map objects names onto properties, attributes, methods
        """
        m = {}
        for k in dir(model):
            try:
                m[k] = getattr(model, k)
            except AttributeError:
                # Sometimes raises an error e.g. "AttributeError: Manager isn't accessible via Request instances"
                # We can safely ignore as we only care about accessible attributes anyway
                pass
        return m

    def _is_django_object_manager(self, possible_manager):
        """
        :param possible_manager:
        :return: True if duck typing tells us that possible_manager is a RelatedManager object
        """
        return hasattr(possible_manager, 'get_or_create') and hasattr(possible_manager, 'get_queryset')

    def _get_fields(self, model):
        model_class = self.model_class
        if not model_class:
            model_class = model.__class__
        try:
            meta = model_class._meta
        except AttributeError:
            raise ValueError(model)
        fields = {}
        all_fields = meta.fields + model_class._meta.many_to_many
        for f in all_fields:
            # Safer not to duck type here I think
            if isinstance(f, Field):
                fields[f.name] = f
        for k, v in self._dir_map(model).items():
            if self._is_django_object_manager(v):
                fields[k] = v
        # noinspection PyUnresolvedReferences
        extra_fields = self._opts['extra_fields']
        for f in extra_fields:
            fields[f] = getattr(model_class, f)
        return fields

    def _get_attr_or_key(self, obj, attr):
        """
        Best efforts at getting hold of a value from an obj/dict
        :param obj: an object or dictionary
        :param attr: an attribute or key
        :return: the value at attribute or key, or None
        """
        value = None
        try:
            value = getattr(obj, attr)
        except AttributeError:
            try:
                value = obj[attr]
            except KeyError:
                pass
        return value

    def _serialisable(self, model):
        django_fields = self._get_fields(model)
        d = {}
        for name, field in django_fields.items():
            value = self._get_attr_or_key(model, name)
            if value is not None:
                if isinstance(field, DateTimeField):
                    # ElasticSearch is ISO Format i.e. 1994-11-05T13:15:30.345Z by default
                    value = value.strftime('%Y%m%dT%H%M%S.%fZ')
                elif isinstance(field, ForeignKey) or \
                        isinstance(field, OneToOneField):
                    value = ESIndexer(value, follow_reverse=False).serialisable
                # NOTE: I know this works for reverse many-to-many, but no idea
                # whether it works for anything else. Can cross that bridge if ever
                # get to it
                elif isinstance(field, ManyToManyField):
                    all_related = list(value.all())
                    value = ESIndexer(all_related).serialisable
                elif self.follow_reverse and (isinstance(field, ForeignRelatedObjectsDescriptor) or \
                                                      self._is_django_object_manager(field)):
                    all_related = list(value.all())
                    value = ESIndexer(all_related, follow_reverse=False).serialisable

            d[name] = value
        return d

    @property
    def serialisable(self):
        """
        :return: a json-serialisable dictionary
        """
        try:
            # many
            res = []
            for model in self.model:
                res.append(self._serialisable(model))
            return res
        except TypeError:
            # singular
            return self._serialisable(self.model)

    def _insert_path(self):
        """
        :return: the path for use in POSTing new data to ES
        """
        index = self.get_index()
        es_type = self._get_es_type()
        path = self.POST.format(index=index, type=es_type)
        return path

    def _http_insert(self, serialisable):
        es = self._get_http_connection()
        path = self._insert_path()
        es.post(path, serialisable)

    def _http_bulk_insert(self, serialisables):
        pass

    def http_insert(self):
        serialisable = self.serialisable
        # I think checking for Iterable is better than duck typing/EAFP in this case?
        if isinstance(serialisable, collections.Iterable):
            self._http_bulk_insert(serialisable)
        else:
            self._http_insert(serialisable)

    def get_index(self):
        """
        :return: the elasticsearch index to use
        """
        index = SilkyConfig().SILKY_ELASTICSEARCH_INDEX or self.index
        return index

    def _get_http_connection(self):
        """
        :return: a rawes connection to the configured elasticsearch instance
        """
        host = SilkyConfig().SILKY_ELASTICSEARCH_HOST
        port = SilkyConfig().SILKY_ELASTICSEARCH_PORT
        return rawes.Elastic('%s:%d' % (host, port))

    def _get_es_type(self):
        """
        :return: the elasticsearch type to use
        """
        es_type = self.es_type
        if not es_type and self.model_class:
            es_type = self.model_class.__name__
        else:
            es_type = self.model.__class__.__name__
        return es_type


class RequestIndexer(ESIndexer):
    queries = ExtraField()