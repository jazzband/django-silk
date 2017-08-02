try:
    # Django>=1.8
    from django.template.context_processors import csrf
except ImportError:
    from django.core.context_processors import csrf

from django.db.models import Sum
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.generic import View

from silk.auth import login_possibly_required, permissions_possibly_required
from silk.models import Request, Response
from silk.request_filters import BaseFilter, filters_from_query_dict


__author__ = 'danielbradburn'


class FilterableRequestsView(View):

    template = ''

    session_key_request_filters = 'request_filters'

    def _get_paths(self):
        return [''] + [x['path'] for x in Request.objects.values('path').distinct()]

    def _get_status_codes(self):
        return [x['status_code'] for x in Response.objects.values('status_code').distinct()]

    def _get_methods(selfs):
        return [x['method'] for x in Request.objects.values('method').distinct()]

    def _get_objects(self, path=None, filters=None):
        if not filters:
            filters = []
        query_set = Request.objects.all()
        if path:
            query_set = query_set.filter(path=path)
        for f in filters:
            query_set = f.contribute_to_query_set(query_set)
            query_set = query_set.filter(f)
        return query_set

    def _get_path_and_filters(self, request):
        path = request.GET.get('path', None)
        raw_filters = request.session.get(self.session_key_request_filters, {})
        filters = self.make_filters(raw_filters)
        return path, raw_filters, filters

    def make_filters(self, raw_filters):
        return [BaseFilter.from_dict(x) for _, x in raw_filters.items()]

    def _create_context(self, request):

        path, raw_filters, filters = self._get_path_and_filters(request)

        context = {
            'request': request,
            'options_paths': self._get_paths(),
            'options_status_codes': self._get_status_codes(),
            'options_methods': self._get_methods(),
            'view_names': [x[0] for x in Request.objects.values_list('view_name').distinct() if x[0]],
            'filters': raw_filters
        }

        context.update(csrf(request))
        if path:
            context['path'] = path

        context['results'] = self._get_objects(path, filters=filters)

        return context

    @method_decorator(login_possibly_required)
    @method_decorator(permissions_possibly_required)
    def get(self, request, *args, **kwargs):
        return render(request, self.template, self._create_context(request))

    @method_decorator(login_possibly_required)
    @method_decorator(permissions_possibly_required)
    def post(self, request, *args, **kwargs):
        filters = filters_from_query_dict(request.POST)
        request.session[self.session_key_request_filters] = {ident: f.as_dict() for ident, f in filters.items()}
        return render(request, self.template, self._create_context(request))
