from django.shortcuts import render_to_response
from django.views.generic import View
from silky.models import Request

__author__ = 'mtford'


class RootView(View):
    show = [5, 10, 25, 100, 250]
    default_show = 25

    order_by = ['Time', 'Path', 'Num. DB Queries', 'Time Spent Overall', 'Time Spent DB']
    defualt_order_by = 'Time'

    def _get_paths(self):
        return [''] + [x['path'] for x in Request.objects.values('path').distinct()]

    def _get_objects(self, show=None, order_by=None, path=None):
        if not show:
            show = self.default_show
        if order_by == 'Time Spent DB':
            # TODO: Is there a way to formulate this without falling back to SQL?
            query = 'SELECT SUM(silky_sqlquery.end_time-silky_sqlquery.start_time)' \
                    'AS total_db_time, silky_request.id ' \
                    'FROM silky_request ' \
                    'INNER JOIN silky_sqlquery ON silky_request.id=silky_sqlquery.request_id \n'
            if path:
                query += 'WHERE path == "%s" \n' % path
            query += 'GROUP BY request_id \n'
            query += 'ORDER BY total_db_time'
            print(query)
            query_set = Request.objects.raw(query)
        else:
            query_set = Request.objects.all()
            if not order_by:
                order_by = self.defualt_order_by
            if order_by == 'Time':
                query_set = query_set.order_by('-start_time')
            elif order_by == 'Path':
                query_set = query_set.order_by('-path')
            elif order_by == 'Num. DB Queries':
                query_set = query_set.order_by('-num_sql_queries')
            elif order_by == 'Time Spent Overall':
                query_set = query_set.extra(
                    select={'total_time': 'silky_request.end_time - silky_request.start_time'}).order_by('-total_time')
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

    def get(self, request):
        return render_to_response('silky/requests.html', self._create_context(request))