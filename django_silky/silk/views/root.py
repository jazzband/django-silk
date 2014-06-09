from django.db.models import Count, Sum
from django.shortcuts import render_to_response
from django.utils.decorators import method_decorator
from django.views.generic import View
from silk import models
from silk.auth import login_possibly_required, permissions_possibly_required

from silk.models import Request


__author__ = 'mtford'


class RootView(View):
    show = [5, 10, 25, 100, 250]
    default_show = 25

    order_by = ['Recent', 'Path', 'Num. Queries', 'Time', 'Time on queries']
    defualt_order_by = 'Recent'

    def _get_paths(self):
        return [''] + [x['path'] for x in Request.objects.values('path').distinct()]


    def _get_objects(self, show=None, order_by=None, path=None):
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
        return list(query_set[:show])

    def _create_context(self, request):
        show = request.GET.get('show', self.default_show)
        order_by = request.GET.get('order_by', self.defualt_order_by)
        if show:
            show = int(show)
        path = request.GET.get('path', None)
        context = {
            'show': show,
            'order_by': order_by,
            'request': request,
            'options_show': self.show,
            'options_order_by': self.order_by,
            'options_paths': self._get_paths()
        }
        if path:
            context['path'] = path
        context['results'] = self._get_objects(show, order_by, path)
        return context

    @method_decorator(login_possibly_required)
    @method_decorator(permissions_possibly_required)
    def get(self, request):
        return render_to_response('silk/requests.html', self._create_context(request))