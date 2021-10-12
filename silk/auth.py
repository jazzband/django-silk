from functools import WRAPPER_ASSIGNMENTS, wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

from silk.config import SilkyConfig


def login_possibly_required(function=None, **kwargs):
    if SilkyConfig().SILKY_AUTHENTICATION:
        return login_required(function, **kwargs)
    return function


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
            else:
                raise PermissionDenied

        return _wrapped_view

    return decorator
