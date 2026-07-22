import os
import shutil

from django.db import transaction
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.generic import View

from silk.auth import login_possibly_required, permissions_possibly_required
from silk.config import SilkyConfig
from silk.models import Profile, Request, Response, SQLQuery
from silk.utils.data_deletion import delete_model


@method_decorator(transaction.non_atomic_requests, name="dispatch")
class ClearDBView(View):

    @method_decorator(login_possibly_required)
    @method_decorator(permissions_possibly_required)
    def get(self, request, *_, **kwargs):
        return render(request, 'silk/clear_db.html')

    @method_decorator(login_possibly_required)
    @method_decorator(permissions_possibly_required)
    def post(self, request, *_, **kwargs):
        context = {}
        cleared = []

        if 'clear_all' in request.POST:
            delete_model(Profile)
            delete_model(SQLQuery)
            delete_model(Response)
            delete_model(Request)
            cleared = ['Response', 'SQLQuery', 'Profile', 'Request']

            if SilkyConfig().SILKY_DELETE_PROFILES:
                dir = SilkyConfig().SILKY_PYTHON_PROFILER_RESULT_PATH
                for files in os.listdir(dir):
                    path = os.path.join(dir, files)
                    try:
                        shutil.rmtree(path)
                    except OSError:
                        os.remove(path)
                cleared.append('profiler files')
        else:
            if 'clear_requests' in request.POST:
                delete_model(SQLQuery)
                delete_model(Response)
                delete_model(Request)
                cleared += ['Response', 'SQLQuery', 'Request']
            if 'clear_profiling' in request.POST:
                delete_model(Profile)
                cleared.append('Profile')

                if SilkyConfig().SILKY_DELETE_PROFILES:
                    dir = SilkyConfig().SILKY_PYTHON_PROFILER_RESULT_PATH
                    for files in os.listdir(dir):
                        path = os.path.join(dir, files)
                        try:
                            shutil.rmtree(path)
                        except OSError:
                            os.remove(path)
                    cleared.append('profiler files')

        if cleared:
            context['msg'] = 'Cleared data for: {}'.format(', '.join(cleared))

        return render(request, 'silk/clear_db.html', context=context)
