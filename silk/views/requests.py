from django.db.models import Sum
from silk.views.filterable_requests_view import FilterableRequestsView
from silk.models import Request, Response


__author__ = 'mtford'


class RequestsView(FilterableRequestsView):
    template = 'silk/requests.html'
    show = [5, 10, 25, 100, 250]
    default_show = 25

    order_by = {
        'start_time': {
            'label': 'Recent',
            'additional_query_filter': None
        },
        'path': {
            'label': 'Path',
            'additional_query_filter': None
        },
        'num_sql_queries': {
            'label': 'Num. Queries',
            'additional_query_filter': None
        },
        'time_taken': {
            'label': 'Time',
            'additional_query_filter': lambda x: x.filter(time_taken__gte=0)
        },
        'db_time': {
            'label': 'Time on queries',
            'additional_query_filter': lambda x: x.annotate(db_time=Sum('queries__time_taken'))
            .filter(db_time__gte=0)
        },
    }
    order_dir = {
        'ASC': {
            'label': 'Ascending'
        },
        'DESC': {
            'label': 'Descending'
        }
    }
    default_order_by = 'start_time'
    default_order_dir = 'DESC'

    session_key_request_filters = 'request_filters'

    @property
    def options_order_by(self):
        return [{'value': x, 'label': self.order_by[x]['label']} for x in self.order_by.keys()]

    @property
    def options_order_dir(self):
        return [{'value': x, 'label': self.order_dir[x]['label']} for x in self.order_dir.keys()]

    def _get_paths(self):
        return [''] + [x['path'] for x in Request.objects.values('path').distinct()]

    def _get_status_codes(self):
        return [x['status_code'] for x in Response.objects.values('status_code').distinct()]

    def _get_methods(self):
        return [x['method'] for x in Request.objects.values('method').distinct()]

    def _extend_queryset(self, query_set, show=None, order_by=None, order_dir=None):
        if not show:
            show = self.default_show
        if not order_by:
            order_by = self.default_order_by
        if not order_dir:
            order_dir = self.default_order_dir
        if order_by not in self.order_by.keys():
            raise RuntimeError('Unknown order_by: "%s"' % order_by)
        ob = self.order_by[order_by]
        if ob['additional_query_filter'] is not None:
            query_set = ob['additional_query_filter'](query_set)
        query_set = query_set.order_by('%s%s' % ('-' if order_dir == 'DESC' else '', order_by))
        return query_set[:show]

    def _create_context(self, request):

        show = request.GET.get('show', self.default_show)
        if show:
            show = int(show)
        order_by = request.GET.get('order_by', self.default_order_by)
        order_dir = request.GET.get('order_dir', self.default_order_dir)

        context = super(RequestsView, self)._create_context(request)
        context['show'] = show
        context['order_by'] = order_by
        context['order_dir'] = order_dir
        context['options_show'] = self.show
        context['options_order_by'] = self.options_order_by
        context['options_order_dir'] = self.options_order_dir
        context['results'] = self._extend_queryset(context['results'], show, order_by, order_dir)

        return context
