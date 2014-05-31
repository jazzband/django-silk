from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.views.generic import View
from silky.models import Request


class Raw(View):

    def get(self, request, request_id):
        typ = request.GET.get('typ', None)
        subtyp = request.GET.get('subtyp', None)
        body = None
        if typ and subtyp:
            silky_request = Request.objects.get(pk=request_id)
            if typ == 'request':
                body = silky_request.raw_body if subtyp == 'raw' else silky_request.body
            elif typ == 'response':
                body = silky_request.response.raw_body if subtyp == 'raw' else silky_request.response.body
            return render_to_response('silky/raw.html', {
                'body': body
            })
        else:
            return HttpResponse(content='Bad Request', status=400)