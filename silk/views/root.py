from django.core.context_processors import csrf

from django.db.models import Sum
from django.shortcuts import render_to_response
from django.utils.decorators import method_decorator
from django.views.generic import View
from silk.profiling.dynamic import _get_module

from silk.auth import login_possibly_required, permissions_possibly_required
from silk.models import Request
from silk.request_filters import BaseFilter


__author__ = 'mtford'


class RootView(View):
    show = [5, 10, 25, 100, 250]
    default_show = 25

    order_by = ['Recent', 'Path', 'Num. Queries', 'Time', 'Time on queries']
    defualt_order_by = 'Recent'

    session_key_request_filters = 'request_filters'

    def _get_paths(self):
        return [''] + [x['path'] for x in Request.objects.values('path').distinct()]


    def _get_objects(self, show=None, order_by=None, path=None, filters=None):
        if not filters:
            filters = []
        if not show:
            show = self.default_show
        query_set = Request.objects.all()
        if not order_by:
            order_by = self.defualt_order_by
        if order_by == 'Recent':
            query_set = query_set.order_by('-start_time')
        elif order_by == 'Path':
            query_set = query_set.order_by('-path')
        elif order_by == 'Num. Queries':
            query_set = query_set.order_by('-num_sql_queries')
        elif order_by == 'Time':
            query_set = query_set.order_by('-time_taken')
        elif order_by == 'Time on queries':
            query_set = query_set.annotate(db_time=Sum('queries__time_taken')).order_by('-db_time')
        else:
            raise RuntimeError('Unknown order_by: "%s"' % order_by)
        if path:
            query_set = query_set.filter(path=path)
        for f in filters:
            query_set = query_set.filter(f)
        return list(query_set[:show])

    def _create_context(self, request):
        show = request.GET.get('show', self.default_show)
        order_by = request.GET.get('order_by', self.defualt_order_by)
        if show:
            show = int(show)
        path = request.GET.get('path', None)
        filters = request.session.get(self.session_key_request_filters, [])
        context = {
            'show': show,
            'order_by': order_by,
            'request': request,
            'options_show': self.show,
            'options_order_by': self.order_by,
            'options_paths': self._get_paths(),
            'view_names': [x[0] for x in Request.objects.values_list('view_name').distinct()],
            'filters': filters
        }
        context.update(csrf(request))
        if path:
            context['path'] = path
        context['results'] = self._get_objects(show, order_by, path, filters=[BaseFilter.from_dict(x) for x in filters])
        return context

    @method_decorator(login_possibly_required)
    @method_decorator(permissions_possibly_required)
    def get(self, request):
        return render_to_response('silk/requests.html', self._create_context(request))

    @method_decorator(login_possibly_required)
    @method_decorator(permissions_possibly_required)
    def post(self, request):
        raw_filters = {}
        for key in request.POST:
            splt = key.split('-')
            if splt[0].startswith('filter'):
                ident = splt[1]
                typ = splt[2]
                if not ident in raw_filters:
                    raw_filters[ident] = {}
                raw_filters[ident][typ] = request.POST[key]
        filters = []
        for _, raw_filter in raw_filters.items():
            typ = raw_filter['typ']
            value = raw_filter['value']
            module = _get_module('silk.request_filters')
            filter_class = getattr(module, typ)
            f = filter_class(value)
            filters.append(f)
        request.session[self.session_key_request_filters] = [x.as_dict() for x in filters]
        return render_to_response('silk/requests.html', self._create_context(request))