from django.shortcuts import render_to_response
from django.views.generic import View
from silky.models import Profile
from silky.views.sql_detail import _code


class ProfilingDetailView(View):
    def get(self, request,  profile_id):
        profile = Profile.objects.get(pk=profile_id)
        file_path = profile.file_path
        line_num = profile.line_num
        context = {
            'profile': profile,
            'line_num': line_num,
            'file_path': file_path,
            'request': request
        }
        if file_path and line_num:
            try:
                actual_line, code = _code(file_path, line_num)
                context['code'] = code
                context['actual_line'] = actual_line
            except IOError, e:
                if e.errno == 2:
                    context['code_error'] = e.filename + ' does not exist.'
                else:
                    raise e

        return render_to_response('silky/profile_detail.html', context)
