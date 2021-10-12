from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.generic import View

from silk.auth import login_possibly_required, permissions_possibly_required
from silk.models import Request


class CProfileView(View):

    @method_decorator(login_possibly_required)
    @method_decorator(permissions_possibly_required)
    def get(self, request, *_, **kwargs):
        request_id = kwargs['request_id']
        silk_request = Request.objects.get(pk=request_id)
        context = {
            'silk_request': silk_request,
            'request': request}

        return render(request, 'silk/cprofile.html', context)
