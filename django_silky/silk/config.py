from copy import copy
from silk.singleton import Singleton
from django.conf import settings

import six


class SilkyConfig(six.with_metaclass(Singleton, object)):

    defaults = {
        'SILKY_DEBUG': False,
        'SILKY_DYNAMIC_PROFILING': []
    }

    def __init__(self):
        super(SilkyConfig, self).__init__()
        options = {option: getattr(settings, option) for option in dir(settings) if option.startswith('SILKY')}
        self.attrs = copy(self.defaults)
        self.attrs.update(options)

    def __getattr__(self, item):
        return self.attrs[item]