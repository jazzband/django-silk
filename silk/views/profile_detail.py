from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.generic import View
from silk.auth import login_possibly_required, permissions_possibly_required
from silk.models import Profile
from silk.views.sql_detail import _code


class ProfilingDetailView(View):

    @method_decorator(login_possibly_required)
    @method_decorator(permissions_possibly_required)
    def get(self, request, *_, **kwargs):
        profile_id = kwargs['profile_id']
        context = {
            'request': request
        }
        profile = Profile.objects.get(pk=profile_id)
        file_path = profile.file_path
        line_num = profile.line_num
        context['profile'] = profile
        context['line_num'] = file_path
        context['file_path'] = line_num
        if profile.request:
            context['silk_request'] = profile.request
        if file_path and line_num:
            try:
                actual_line, code = _code(file_path, line_num, profile.end_line_num)
                context['code'] = code
                context['actual_line'] = actual_line
            except IOError as e:
                if e.errno == 2:
                    context['code_error'] = e.filename + ' does not exist.'
                else:
                    raise e

        return render(request, 'silk/profile_detail.html', context)
