from copy import copy
from silk.singleton import Singleton

import six


class SilkyConfig(six.with_metaclass(Singleton, object)):

    defaults = {
        'SILKY_DYNAMIC_PROFILING': [],
        'SILKY_IGNORE_PATHS': [],
        'SILKY_HIDE_COOKIES': True
    }

    def _setup(self):
        from django.conf import settings
        options = {option: getattr(settings, option) for option in dir(settings) if option.startswith('SILKY')}
        self.attrs = copy(self.defaults)
        self.attrs.update(options)

    def __init__(self):
        super(SilkyConfig, self).__init__()
        self._setup()

    def __getattr__(self, item):
        return self.attrs[item]