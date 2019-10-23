from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.generic import View
from silk.auth import login_possibly_required, permissions_possibly_required


class ClearDBView(View):

    @method_decorator(login_possibly_required)
    @method_decorator(permissions_possibly_required)
    def get(self, request, *_, **kwargs):
        return render(request, 'silk/clear_db.html')

    @method_decorator(login_possibly_required)
    @method_decorator(permissions_possibly_required)
    def post(self, request, *_, **kwargs):

        return render(request, 'silk/clear_db.html')
