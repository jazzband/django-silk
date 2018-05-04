import csv
import contextlib
from six import StringIO
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from silk.models import Request
from silk.views.filterable_requests_view import FilterableRequestsView
from silk.auth import login_possibly_required, permissions_possibly_required
from silk.request_filters import filters_from_query_dict


class DistributionView(FilterableRequestsView):
    template = 'silk/distribution.html'

    @method_decorator(login_possibly_required)
    @method_decorator(permissions_possibly_required)
    def get(self, request, *args, **kwargs):
        group_by = kwargs.get('group_by', None) or 'start_time'
        context = self._create_context(request)
        context.update(group_by=group_by)
        return render(request, self.template, context)


class DistributionDataView(FilterableRequestsView):

    def to_csv(self, queryset):
        with contextlib.closing(StringIO()) as stream:
            writer = csv.writer(stream, delimiter=',')
            writer.writerow(('group', 'value'))
            writer.writerows(queryset)
            return stream.getvalue().encode('utf-8')

    @method_decorator(login_possibly_required)
    @method_decorator(permissions_possibly_required)
    def get(self, request):

        path, _, filters = self._get_path_and_filters(request)
        group_by = request.GET.get('group-by', None) or 'date'

        # properties can't be used in values_list
        get_group = lambda x: x
        if group_by in ('date', 'start', 'hour', 'minute'):
            get_group = getattr(Request, 'get_' + group_by)
            group_by = 'start_time'

        fields = group_by, 'time_taken'
        queryset = self._get_objects(path, filters).values_list(*fields).order_by(group_by)
        csv = self.to_csv((get_group(group), value) for group, value in queryset)

        return HttpResponse(csv, content_type='text/csv')

