from copy import copy
from silky.singleton import Singleton
from django.conf import settings




class SilkyConfig(object):
    __metaclass__ = Singleton

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