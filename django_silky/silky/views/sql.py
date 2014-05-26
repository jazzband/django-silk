from django.shortcuts import render_to_response
from django.views.generic import View
from silky.models import Request, SQLQuery
from silky.utils.pagination import _page

__author__ = 'mtford'


class SQLView(View):
    def get(self, request, request_id):
        r = Request.objects.get(id=request_id)
        query_set = SQLQuery.objects.filter(request=r).order_by('-start_time')
        page = _page(request, query_set)
        return render_to_response('silky/sql.html', {
            'items': page,
            'request': request,
            'r': r
        })