from django.shortcuts import render_to_response
from django.views.generic import View
from silky.models import Request, SQLQuery, Profile
from silky.utils.pagination import _page
from silky.views.method_map_view import MethodMapView

__author__ = 'mtford'


class SQLView(View):

    def get(self, request, *_, **kwargs):
        request_id = kwargs.get('request_id')
        profile_id = kwargs.get('profile_id')
        context = {
            'request': request,
        }
        if request_id:
            r = Request.objects.get(id=request_id)
            query_set = SQLQuery.objects.filter(request=r).order_by('-start_time')
            page = _page(request, query_set)
            context['r'] = r
        elif profile_id:
            p = Profile.objects.get(id=profile_id)
            page = _page(request, p.queries.order_by('-start_time').all())
            context['profile'] = p
        else:
            raise KeyError('No profile_id or request_id')
        context['items'] = page
        return render_to_response('silky/sql.html', context)

