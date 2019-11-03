from functools import lru_cache
from copy import copy
from importlib import import_module

from django.utils import six

from silk.singleton import Singleton


def default_permissions(user):
    if user:
        return user.is_staff
    return False


class SilkyConfig(six.with_metaclass(Singleton, object)):
    defaults = {
        'SILKY_DYNAMIC_PROFILING': [],
        'SILKY_IGNORE_PATHS': [],
        'SILKY_HIDE_COOKIES': True,
        'SILKY_IGNORE_QUERIES': [],
        'SILKY_META': False,
        'SILKY_AUTHENTICATION': False,
        'SILKY_AUTHORISATION': False,
        'SILKY_PERMISSIONS': default_permissions,
        'SILKY_MAX_RECORDED_REQUESTS': 10 ** 4,
        'SILKY_MAX_RECORDED_REQUESTS_CHECK_PERCENT': 10,
        'SILKY_MAX_REQUEST_BODY_SIZE': -1,
        'SILKY_MAX_RESPONSE_BODY_SIZE': -1,
        'SILKY_INTERCEPT_PERCENT': 100,
        'SILKY_INTERCEPT_FUNC': None,
        'SILKY_PYTHON_PROFILER': False,
        'SILKY_STORAGE_CLASS': 'silk.storage.ProfilerResultStorage',
        'SILKY_MIDDLEWARE_CLASS': 'silk.middleware.SilkyMiddleware',
        'SILKY_REQUEST_MODEL_FACTORY_CLASS': 'silk.model_factory.RequestModelFactory',
        'SILKY_RESPONSE_MODEL_FACTORY_CLASS': 'silk.model_factory.ResponseModelFactory',
    }

    def _setup(self):
        from django.conf import settings

        options = {option: getattr(settings, option) for option in dir(settings) if option.startswith('SILKY')}
        self.attrs = copy(self.defaults)
        self.attrs['SILKY_PYTHON_PROFILER_RESULT_PATH'] = settings.MEDIA_ROOT
        self.attrs.update(options)

    @staticmethod
    @lru_cache()
    def _load_class(cls_name):
        mod_name, cls_name = cls_name.rsplit('.', 1)
        mod = import_module(mod_name)
        return getattr(mod, cls_name)

    @property
    def request_model_factory(self):
        return self._load_class(self.SILKY_REQUEST_MODEL_FACTORY_CLASS)

    @property
    def response_model_factory(self):
        return self._load_class(self.SILKY_RESPONSE_MODEL_FACTORY_CLASS)

    def __init__(self):
        super(SilkyConfig, self).__init__()
        self._setup()

    def __getattr__(self, item):
        return self.attrs.get(item, None)

    def __setattribute__(self, key, value):
        self.attrs[key] = value
