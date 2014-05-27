import json

from django.shortcuts import render_to_response
from django.views.generic import View

from silky.code_generation.curl import curl_cmd
from silky.models import Request
from silky.code_generation.django_test_client import gen


class RequestView(View):
    def get(self, request, request_id):
        silky_request = Request.objects.get(pk=request_id)
        query_params = None
        if silky_request.query_params:
            query_params = json.loads(silky_request.query_params)
        context = {
            'silky_request': silky_request,
            'curl': curl_cmd(url=request.build_absolute_uri(silky_request.path),
                             method=silky_request.method,
                             query_params=query_params,
                             body=silky_request.body,
                             content_type=silky_request.content_type),
            'query_params': json.dumps(query_params, sort_keys=True, indent=4),
            'client': gen(path=silky_request.path,
                          method=silky_request.method,
                          query_params=query_params,
                          data=silky_request.body,
                          content_type=silky_request.content_type),
            'request': request
        }
        return render_to_response('silky/request.html', context)




