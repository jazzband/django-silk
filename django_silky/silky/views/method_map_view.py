from functools import update_wrapper
from django.views.generic import View


class MethodMapView(View):
    @classmethod
    def as_view(cls, method_map=None, **initkwargs):
        if method_map:
            # NOTE: The below has been taken from super.as_view.
            # If that code changes this will also need to be updated. The only thing modified
            # below is the mapping of methods.
            def view(request, *args, **kwargs):
                self = cls(**initkwargs)
                # The below mapping allows us to use this class for multiple URL patterns
                for http_method, method in method_map.items():
                    setattr(self, http_method, getattr(self, method))
                if hasattr(self, 'get') and not hasattr(self, 'head'):
                    self.head = self.get
                self.request = request
                self.args = args
                self.kwargs = kwargs
                return self.dispatch(request, *args, **kwargs)
            update_wrapper(view, cls, updated=())
            update_wrapper(view, cls.dispatch, assigned=())
            return view
        else:
            return super(MethodMapView, cls).as_view(**initkwargs)