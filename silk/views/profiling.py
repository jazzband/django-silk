from django.core.context_processors import csrf
from django.db.models import Count, Sum
from django.shortcuts import render_to_response
from django.utils.decorators import method_decorator
from django.views.generic import View
from silk.auth import login_possibly_required, permissions_possibly_required

from silk.models import Profile, Request
from silk.profiling.dynamic import _get_module
from silk.request_filters import BaseFilter


class ProfilingView(View):
    show = [5, 10, 25, 100, 250]
    default_show = 25
    order_by = ['Recent',
                'Name',
                'Function Name',
                'Num. Queries',
                'Time',
                'Time on queries']
    defualt_order_by = 'Recent'
    session_key_profile_filters = 'session_key_profile_filters'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def _get_distinct_values(self, field, silk_request):
        if silk_request:
            query_set = Profile.objects.filter(request=silk_request)
        else:
            query_set = Profile.objects.all()
        function_names = [x[field] for x in query_set.values(field).distinct()]
        # Ensure top, default option is ''
        try:
            function_names.remove('')
        except ValueError:
            pass
        function_names = [''] + function_names
        return function_names

    def _get_function_names(self, silk_request=None):
        return self._get_distinct_values('func_name', silk_request)

    def _get_names(self, silk_request=None):
        return self._get_distinct_values('name', silk_request)

    def _get_objects(self, show=None, order_by=None, name=None, func_name=None, silk_request=None, filters=None):
        if not filters:
            filters = []
        if not show:
            show = self.default_show
        manager = Profile.objects
        if silk_request:
            query_set = manager.filter(request=silk_request)
        else:
            query_set = manager.all()
        if not order_by:
            order_by = self.defualt_order_by
        if order_by == 'Recent':
            query_set = query_set.order_by('-start_time')
        elif order_by == 'Name':
            query_set = query_set.order_by('-name')
        elif order_by == 'Function Name':
            query_set = query_set.order_by('-func_name')
        elif order_by == 'Num. Queries':
            query_set = query_set.annotate(num_queries=Count('queries')).order_by('-num_queries')
        elif order_by == 'Time':
            query_set = query_set.order_by('-time_taken')
        elif order_by == 'Time on queries':
            query_set = query_set.annotate(db_time=Sum('queries__time_taken')).order_by('-db_time')
        elif order_by:
            raise RuntimeError('Unknown order_by: "%s"' % order_by)
        if func_name:
            query_set = query_set.filter(func_name=func_name)
        if name:
            query_set = query_set.filter(name=name)
        for f in filters:
            query_set = query_set.filter(f)
        return list(query_set[:show])

    def _create_context(self, request, *args, **kwargs):
        request_id = kwargs.get('request_id')
        if request_id:
            silk_request = Request.objects.get(pk=request_id)
        else:
            silk_request = None
        show = request.GET.get('show', self.default_show)
        order_by = request.GET.get('order_by', self.defualt_order_by)
        if show:
            show = int(show)
        func_name = request.GET.get('func_name', None)
        name = request.GET.get('name', None)
        filters = request.session.get(self.session_key_profile_filters, [])
        context = {
            'show': show,
            'order_by': order_by,
            'request': request,
            'func_name': func_name,
            'options_show': self.show,
            'options_order_by': self.order_by,
            'options_func_names': self._get_function_names(silk_request),
            'options_names': self._get_names(silk_request),
            'filters': filters
        }
        context.update(csrf(request))
        if silk_request:
            context['silk_request'] = silk_request
        if func_name:
            context['func_name'] = func_name
        if name:
            context['name'] = name

        objs = self._get_objects(show=show,
                                 order_by=order_by,
                                 func_name=func_name,
                                 silk_request=silk_request,
                                 name=name,
                                 filters=[BaseFilter.from_dict(x) for x in filters])
        context['results'] = objs
        return context

    @method_decorator(login_possibly_required)
    @method_decorator(permissions_possibly_required)

    def get(self, request, *args, **kwargs):
        return render_to_response('silk/profiling.html', self._create_context(request, *args, **kwargs))

    @method_decorator(login_possibly_required)
    @method_decorator(permissions_possibly_required)
    def post(self, request):
        raw_filters = {}
        for key in request.POST:
            splt = key.split('-')
            if splt[0].startswith('filter'):
                ident = splt[1]
                typ = splt[2]
                if not ident in raw_filters:
                    raw_filters[ident] = {}
                raw_filters[ident][typ] = request.POST[key]
        filters = []
        for _, raw_filter in raw_filters.items():
            typ = raw_filter['typ']
            value = raw_filter['value']
            module = _get_module('silk.request_filters')
            filter_class = getattr(module, typ)
            f = filter_class(value)
            filters.append(f)
        request.session[self.session_key_profile_filters] = [x.as_dict() for x in filters]
        return render_to_response('silk/profiling.html', self._create_context(request))
