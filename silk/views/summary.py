from django.db.models import Avg, Count, Sum, Max
from django.shortcuts import render_to_response

from django.utils.decorators import method_decorator
from django.views.generic import View

from silk import models

from silk.auth import login_possibly_required, permissions_possibly_required


class SummaryView(View):
    def _avg_num_queries(self):
        queries__aggregate = models.Request.objects.annotate(num_queries=Count('queries')).aggregate(num=Avg('num_queries'))
        return queries__aggregate['num']

    def _avg_time_spent_on_queries(self):
        taken__aggregate = models.Request.objects.annotate(time_spent=Sum('queries__time_taken')).aggregate(num=Avg('time_spent'))
        return taken__aggregate['num']

    def _avg_overall_time(self):
        taken__aggregate = models.Request.objects.annotate(time_spent=Sum('time_taken')).aggregate(num=Avg('time_spent'))
        return taken__aggregate['num']

    def _longest_query_by_view(self):
        r = models.Request.objects.values_list("view_name").annotate(max=Max('time_taken')).order_by('-max')[:4]
        requests = []
        for view_name, max in r:
            request = models.Request.objects.get(time_taken=max, view_name=view_name)
            requests.append(request)
        return requests

    def _time_spent_in_db_by_view(self):
        queryset = models.Request.objects.values_list('view_name').annotate(t=Sum('queries__time_taken')).order_by('-t')
        views = [r[0] for r in queryset[:4]]
        requests = []
        for view in views:
            try:
                r = models.Request.objects.filter(view_name=view).annotate(t=Sum('queries__time_taken')).order_by('-t')[0]
                requests.append(r)
            except IndexError:
                pass
        return requests

    def _num_queries_by_view(self):
        queryset = models.Request.objects.values_list('view_name').annotate(t=Count('queries')).order_by('-t')
        views = [r[0] for r in queryset[:4]]
        requests = []
        for view in views:
            try:
                r = models.Request.objects.filter(view_name=view).annotate(t=Count('queries')).order_by('-t')[0]
                requests.append(r)
            except IndexError:
                pass
        return requests

    @method_decorator(login_possibly_required)
    @method_decorator(permissions_possibly_required)
    def get(self, request):
        avg_overall_time = self._avg_num_queries()
        c = {
            'request': request,
            'num_requests': models.Request.objects.all().count(),
            'num_profiles': models.Profile.objects.all().count(),
            'avg_num_queries': avg_overall_time,
            'avg_time_spent_on_queries': self._avg_time_spent_on_queries(),
            'avg_overall_time': self._avg_overall_time(),
            'longest_queries_by_view': self._longest_query_by_view(),
            'most_time_spent_in_db': self._time_spent_in_db_by_view(),
            'most_queries': self._num_queries_by_view()
        }
        return render_to_response('silk/summary.html', c)