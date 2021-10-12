__author__ = 'mtford'


class Singleton(type, metaclass=object):
    def __init__(cls, name, bases, d):
        super().__init__(name, bases, d)
        cls.instance = None

    def __call__(cls, *args):
        if cls.instance is None:
            cls.instance = super().__call__(*args)
        return cls.instance
