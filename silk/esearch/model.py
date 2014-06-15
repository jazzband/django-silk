"""
Provision serialisation of django models/dictionaries to Elasticsearch.

It's rather inefficient at the moment in that relations are nested JSON. This is fine
in that we never actually modify anything after the fact and so it's time efficient.
What it gains in time, we lose in space efficiency however.
"""
from django.db.models import ForeignKey, ManyToManyField, OneToOneField, DateTimeField
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
    and Elasticsearch
    """
    model_class = None
    index = None

    def __init__(self, model):
        """
        :param model: a dictionary or an object, doesn't matter
        """
        super(ESIndexer, self).__init__()
        self.model = model

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
            fields[f.name] = f
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
                    value = ESIndexer(value).serialisable
                # NOTE: I know this works for reverse many-to-many, but no idea
                # whether it works for anything else. Can cross that bridge if ever
                # get to it
                elif isinstance(field, ManyToManyField) or \
                        isinstance(field, ForeignRelatedObjectsDescriptor):
                    # noinspection PyUnresolvedReferences
                    all_related = list(value.all())
                    value = ESIndexer(all_related).serialisable
            d[name] = value
        return d

    @property
    def serialisable(self):
        """
        :return: a json-serialisable dictionary
        """
        try:
            res = []
            for model in self.model:
                res.append(self._serialisable(model))
            return res
        except TypeError:
            return self._serialisable(self.model)

    def _insert(self, serialisable):
        pass

    def _bulk_insert(self, serialisables):
        pass

    def index(self):
        serialisables = self.serialisable
        host = SilkyConfig().SILKY_ELASTICSEARCH_HOST
        port = SilkyConfig().SILKY_ELASTICSEARCH_PORT
        es = rawes.Elastic('%s:%d' % (host, port))
        es_type = self.index
        if not es_type and self.model_class:
            es_type = self.model_class.__name__
        else:
            es_type = self.model.__class__.__name__
        index = SilkyConfig().SILKY_ELASTICSEARCH_INDEX



class RequestIndexer(ESIndexer):
    queries = ExtraField()