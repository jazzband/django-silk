from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.views.generic import View
from silk.models import Request


class Raw(View):

    def get(self, request, request_id):
        typ = request.GET.get('typ', None)
        subtyp = request.GET.get('subtyp', None)
        body = None
        if typ and subtyp:
            silk_request = Request.objects.get(pk=request_id)
            if typ == 'request':
                body = silk_request.raw_body if subtyp == 'raw' else silk_request.body
            elif typ == 'response':
                body = silk_request.response.raw_body if subtyp == 'raw' else silk_request.response.body
            return render_to_response('silk/raw.html', {
                'body': body
            })
        else:
            return HttpResponse(content='Bad Request', status=400)