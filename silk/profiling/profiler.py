import inspect
import logging
import time

from django.conf import settings
from django.utils import timezone
import six

from silk.collector import DataCollector


Logger = logging.getLogger('silk')


# noinspection PyPep8Naming
class silk_profile(object):
    def __init__(self, name=None, _dynamic=False):
        self.name = name
        self.profile = None
        self._queries_before = None
        self._queries_after = None
        self._dynamic = _dynamic

    def _query_identifiers_from_collector(self):
        return [x for x in DataCollector().queries]

    def _start_queries(self):
        self._queries_before = self._query_identifiers_from_collector()

    def __enter__(self):
        if self._silk_installed() and self._should_profile():
            self._start_queries()
            if not self.name:
                raise ValueError('silk_profile used as a context manager must have a name')
            frame = inspect.currentframe()
            frames = inspect.getouterframes(frame)
            outer_frame = frames[1]
            path = outer_frame[1]
            line_num = outer_frame[2]
            self.profile = {
                'name': self.name,
                'file_path': path,
                'line_num': line_num,
                'dynamic': self._dynamic,
                'request': DataCollector().request,
                'start_time': timezone.now(),
            }
        else:
            Logger.warn('Cannot execute silk_profile as silk is not installed correctly.')

    def _finalise_queries(self):
        collector = DataCollector()
        self._queries_after = self._query_identifiers_from_collector()
        assert self.profile, 'no profile was created'
        diff = set(self._queries_after).difference(set(self._queries_before))
        self.profile['queries'] = diff
        collector.register_profile(self.profile)

    # noinspection PyUnusedLocal
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._silk_installed() and self._should_profile():
            exception_raised = exc_type is not None
            self.profile['exception_raised'] = exception_raised
            self.profile['end_time'] = timezone.now()
            self._finalise_queries()

    def _silk_installed(self):
        app_installed = 'silk' in settings.INSTALLED_APPS
        middleware_installed = 'silk.middleware.SilkyMiddleware' in settings.MIDDLEWARE_CLASSES
        return app_installed and middleware_installed

    def _should_profile(self):
        return DataCollector().request is not None

    def __call__(self, target):
        if self._silk_installed():
            def wrapped_target(*args, **kwargs):
                try:
                    func_code = six.get_function_code(target)
                except AttributeError:
                    raise NotImplementedError('Profile not implemented to decorate type %s' % target.__class__.__name__)
                line_num = func_code.co_firstlineno
                file_path = func_code.co_filename
                func_name = target.__name__
                if not self.name:
                    self.name = func_name
                self.profile = {
                    'func_name': func_name,
                    'name': self.name,
                    'file_path': file_path,
                    'line_num': line_num,
                    'dynamic': self._dynamic,
                    'start_time': timezone.now(),
                    'request': DataCollector().request
                }
                self._start_queries()
                try:
                    result = target(*args, **kwargs)
                except Exception:
                    self.profile['exception_raised'] = True
                    raise
                finally:
                    self.profile['end_time'] = timezone.now()
                    self._finalise_queries()
                return result

            return wrapped_target
        else:
            Logger.warn('Cannot execute silk_profile as silk is not installed correctly.')
            return target

    def distinct_queries(self):
        queries = [x for x in self._queries_after if not x in self._queries_before]
        return queries


@silk_profile()
def blah():
    time.sleep(1)


if __name__ == '__main__':
    blah()