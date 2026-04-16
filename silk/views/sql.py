from django.shortcuts import get_object_or_404, render
from django.utils.decorators import method_decorator
from django.views.generic import View

from silk.auth import login_possibly_required, permissions_possibly_required
from silk.models import Profile, Request, SQLQuery
from silk.utils.n_plus_one import detect_n_plus_one
from silk.utils.pagination import _page

__author__ = 'mtford'


class SQLView(View):
    page_sizes = [5, 10, 25, 100, 200, 500, 1000]
    default_page_size = 200

    @method_decorator(login_possibly_required)
    @method_decorator(permissions_possibly_required)
    def get(self, request, *_, **kwargs):
        request_id = kwargs.get('request_id')
        profile_id = kwargs.get('profile_id')
        per_page_param = request.GET.get('per_page')
        if per_page_param is not None:
            try:
                per_page = int(per_page_param)
            except (TypeError, ValueError):
                per_page = self.default_page_size
            request.session['silk_sql_per_page'] = per_page
        else:
            try:
                per_page = int(request.session.get('silk_sql_per_page', self.default_page_size))
            except (TypeError, ValueError):
                per_page = self.default_page_size
        context = {
            'request': request,
            'options_page_size': self.page_sizes,
            'per_page': per_page,
        }
        if request_id:
            silk_request = get_object_or_404(Request, id=request_id)
            all_queries = list(SQLQuery.objects.filter(request=silk_request).order_by('-start_time'))
            for q in all_queries:
                q.start_time_relative = q.start_time - silk_request.start_time
            n_plus_one = detect_n_plus_one(all_queries)
            page = _page(request, all_queries, per_page)
            context['silk_request'] = silk_request
            context['n_plus_one'] = n_plus_one
            context['n_plus_one_ids'] = n_plus_one.flagged_query_ids
        if profile_id:
            p = get_object_or_404(Profile, id=profile_id)
            page = _page(request, p.queries.order_by('-start_time').all(), per_page)
            context['profile'] = p
        if not (request_id or profile_id):
            raise KeyError('no profile_id or request_id')
        # noinspection PyUnboundLocalVariable
        context['items'] = page
        return render(request, 'silk/sql.html', context)
