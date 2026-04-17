from functools import WRAPPER_ASSIGNMENTS, wraps

from django.http import Http404

from silk.config import SilkyConfig


def login_possibly_required(function=None, **kwargs):
    if not SilkyConfig().SILKY_AUTHENTICATION:
        return function

    @wraps(function, assigned=WRAPPER_ASSIGNMENTS)
    def _wrapped_view(request, *args, **kw):
        if not request.user.is_authenticated:
            raise Http404
        return function(request, *args, **kw)

    return _wrapped_view


def permissions_possibly_required(function=None):
    if SilkyConfig().SILKY_AUTHORISATION:
        actual_decorator = user_passes_test(
            SilkyConfig().SILKY_PERMISSIONS
        )
        if function:
            return actual_decorator(function)
        return actual_decorator
    return function


def user_passes_test(test_func):
    def decorator(view_func):
        @wraps(view_func, assigned=WRAPPER_ASSIGNMENTS)
        def _wrapped_view(request, *args, **kwargs):
            if test_func(request.user):
                return view_func(request, *args, **kwargs)
            raise Http404

        return _wrapped_view

    return decorator
