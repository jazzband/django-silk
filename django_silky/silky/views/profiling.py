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
from django.shortcuts import render_to_response
from django.views.generic import View
from silky.models import Profile, Request


class ProfilingView(View):
    show = [5, 10, 25, 100, 250]
    default_show = 25
    order_by = ['Time',
                'Name',
                'Function Name']
    defualt_order_by = 'Name'

    def _get_function_names(self):
        return [''] + [x['func_name'] for x in Profile.objects.values('func_name').distinct()]

    def _get_objects(self, show=None, order_by=None, func_name=None, silky_request=None):
        if not show:
            show = self.default_show
        manager = Profile.objects
        if silky_request:
            query_set = manager.filter(request=silky_request)
        else:
            query_set = manager.all()
        if not order_by:
            order_by = self.defualt_order_by
        if order_by == 'Time':
            query_set = query_set.order_by('-start_time')
        elif order_by == 'Name':
            query_set = query_set.order_by('-name')
        elif order_by == 'Function Name':
            query_set = query_set.order_by('-func_name')
        elif order_by:
            raise RuntimeError('Unknown order_by: "%s"' % order_by)
        if func_name:
            query_set = query_set.filter(func_name=func_name)
        return list(query_set[:show])

    def _create_context(self, request, *args, **kwargs):
        request_id = kwargs.get('request_id')
        if request_id:
            silky_request = Request.objects.get(pk=request_id)
        else:
            silky_request = None
        show = request.GET.get('show', self.default_show)
        order_by = request.GET.get('order_by', self.defualt_order_by)
        if show:
            show = int(show)
        path = request.GET.get('path', None)
        context = {
            'show': show,
            'order_by': order_by,
            'request': request,
            'options_show': self.show,
            'options_order_by': self.order_by,
            'options_func_names': self._get_function_names(),
        }
        if silky_request:
            context['silky_request'] = silky_request
        if path:
            context['path'] = path

        objs = self._get_objects(show, order_by, path, silky_request)
        context['results'] = objs
        return context

    def get(self, request, *args, **kwargs):
        return render_to_response('silky/profiling.html', self._create_context(request, *args, **kwargs))
