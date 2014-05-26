from django.shortcuts import render_to_response
from django.views.generic import View
from silky.models import Request, SQLQuery, Profile
from silky.utils.pagination import _page
from silky.views.method_map_view import MethodMapView

__author__ = 'mtford'


class SQLView(MethodMapView):

    def get_request(self, request, request_id):
        r = Request.objects.get(id=request_id)
        query_set = SQLQuery.objects.filter(request=r).order_by('-start_time')
        page = _page(request, query_set)
        return render_to_response('silky/sql.html', {
            'items': page,
            'request': request,
            'r': r
        })

    def get_profile(self, request, profile_id):
        p = Profile.objects.get(id=profile_id)
        page = _page(request, p.queries.order_by('-start_time').all())
        return render_to_response('silky/sql.html', {
            'items': page,
            'request': request,
            'profile': p
        })