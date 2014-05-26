import json

from django.shortcuts import render_to_response
from django.views.generic import View

from silky.code_generation.curl import curl_cmd
from silky.models import Request
from silky.code_generation.django_test_client import gen


class RequestView(View):
    def get(self, request, request_id):
        r = Request.objects.get(pk=request_id)
        query_params = None
        if r.query_params:
            query_params = json.loads(r.query_params)
        context = {
            'r': r,
            'curl': curl_cmd(url=request.build_absolute_uri(r.path),
                             method=r.method,
                             query_params=query_params,
                             body=r.body,
                             content_type=r.content_type),
            'query_params': json.dumps(query_params, sort_keys=True, indent=4),
            'client': gen(path=r.path,
                          method=r.method,
                          query_params=query_params,
                          data=r.body,
                          content_type=r.content_type),
            'request': request
        }

        if r.body:
            if r.content_type:
                content_type = r.content_type.split(';')[0]
                # if content_type in SilkyMiddleware.content_types_json:
                #     context['body'] = json.dumps(json.loads(r.body), sort_keys=True, indent=4)
                # else:
                #     context['body'] = r.body
        return render_to_response('silky/request.html', context)




