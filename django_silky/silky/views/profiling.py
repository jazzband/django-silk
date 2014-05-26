# def profiling(request, request_id):
#     r = Request.objects.get(pk=request_id)
#     query_set = Profile.objects.filter(request=r).order_by('-start_time')
#     page = _page(request, query_set)
#     return render_to_response('silky/profiling.html', {
#         'request': r,
#         'profiles': page
#     })
#
#
# def profile(request, profile_id):
#     profile = Profile.objects.get(pk=profile_id)
#     context = {'profile': profile}
#     if profile.file_path and profile.line_num:
#         context['rendered_code'] = _code_context(profile.file_path, profile.line_num)
#     return render_to_response('silky/profile.html', context)
from django.views.generic import View


class ProfilingView(View):
    pass