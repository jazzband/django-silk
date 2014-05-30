from django.shortcuts import render_to_response
from django.views.generic import View
from silky.models import Profile, Request
from silky.views.sql_detail import _code


class ProfilingDetailView(View):
    def get(self, request,  *_, **kwargs):
        profile_id = kwargs['profile_id']
        silky_request_id = kwargs.get('request_id', None)
        context = {
            'request': request
        }
        profile = Profile.objects.get(pk=profile_id)
        file_path = profile.file_path
        line_num = profile.line_num
        context['profile'] = profile
        context['line_num'] = file_path
        context['file_path'] = line_num
        if silky_request_id:
            silky_request = Request.objects.get(pk=silky_request_id)
            context['silky_request'] = silky_request
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

        return render_to_response('silky/profile_detail.html', context)
