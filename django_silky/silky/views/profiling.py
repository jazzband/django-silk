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

    def _get_distinct_values(self, field, silky_request):
        if silky_request:
            query_set = Profile.objects.filter(request=silky_request)
        else:
            query_set = Profile.objects.all()
        function_names = [x[field] for x in query_set.values(field).distinct()]
        if not '' in function_names:
            function_names = [''] + function_names
        return function_names

    def _get_function_names(self, silky_request=None):
        return self._get_distinct_values('func_name', silky_request)

    def _get_names(self, silky_request=None):
        return self._get_distinct_values('name', silky_request)

    def _get_objects(self, show=None, order_by=None, name=None, func_name=None, silky_request=None):
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
        if func_name is not None:
            query_set = query_set.filter(func_name=func_name)
        if name is not None:
            query_set = query_set.filter(name=name)
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
        func_name = request.GET.get('func_name', None)
        name = request.GET.get('name', None)
        context = {
            'show': show,
            'order_by': order_by,
            'request': request,
            'options_show': self.show,
            'options_order_by': self.order_by,
            'options_func_names': self._get_function_names(silky_request),
            'options_names': self._get_names(silky_request),
        }
        if silky_request:
            context['silky_request'] = silky_request
        if func_name:
            context['func_name'] = func_name
        if name:
            context['name'] = name
        objs = self._get_objects(show=show,
                                 order_by=order_by,
                                 func_name=func_name,
                                 silky_request=silky_request,
                                 name=name)
        context['results'] = objs
        return context

    def get(self, request, *args, **kwargs):
        return render_to_response('silky/profiling.html', self._create_context(request, *args, **kwargs))
