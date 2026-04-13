import json

from django.db.models import Sum
from django.shortcuts import render
from django.template.context_processors import csrf
from django.utils.decorators import method_decorator
from django.views.generic import View

from silk.auth import login_possibly_required, permissions_possibly_required
from silk.models import Request, Response, SQLQuery
from silk.request_filters import (TIME_RANGE_PRESETS, BaseFilter,
                                  FiltersManager, filters_from_request)
from silk.utils.n_plus_one import fingerprint_query
from silk.utils.pagination import get_page

__author__ = 'mtford'

# Sort options: maps field key → display label + optional queryset transform
SORT_OPTIONS = {
    'start_time': {
        'label': 'Recent',
        'additional_query_filter': None,
    },
    'path': {
        'label': 'Path',
        'additional_query_filter': None,
    },
    'num_sql_queries': {
        'label': 'Num. Queries',
        'additional_query_filter': None,
    },
    'time_taken': {
        'label': 'Time',
        'additional_query_filter': lambda qs: qs.filter(time_taken__gte=0),
    },
    'db_time': {
        'label': 'DB Time',
        'additional_query_filter': lambda qs: qs.annotate(
            db_time=Sum('queries__time_taken')
        ).filter(db_time__gte=0),
    },
}

DEFAULT_SORT_LIST = [{'field': 'start_time', 'dir': 'DESC'}]
DEFAULT_PER_PAGE = 25
PER_PAGE_OPTIONS = [10, 25, 50, 100]
SESSION_KEY_FILTERS = 'request_filters'
SESSION_KEY_SORT = 'request_sort'


def _apply_sort(query_set, sort_list):
    """Apply a list of {field, dir} dicts as ORDER BY to *query_set*.

    Annotations are applied per-field (they're additive), but all ORDER BY
    columns are passed in a single .order_by() call so they compound rather
    than replace each other.
    """
    order_fields = []
    for item in sort_list:
        field = item.get('field', 'start_time')
        direction = item.get('dir', 'DESC')
        if field not in SORT_OPTIONS:
            continue
        opt = SORT_OPTIONS[field]
        if opt['additional_query_filter'] is not None:
            query_set = opt['additional_query_filter'](query_set)
        prefix = '-' if direction == 'DESC' else ''
        order_fields.append(f'{prefix}{field}')
    if order_fields:
        query_set = query_set.order_by(*order_fields)
    return query_set


class RequestsView(View):
    # Keep legacy attributes for backward compatibility
    show = PER_PAGE_OPTIONS
    default_show = DEFAULT_PER_PAGE

    order_by = {
        k: {'label': v['label'], 'additional_query_filter': v['additional_query_filter']}
        for k, v in SORT_OPTIONS.items()
    }
    order_dir = {
        'ASC': {'label': 'Ascending'},
        'DESC': {'label': 'Descending'},
    }
    view_style = {
        'card': {'label': 'Cards'},
        'row': {'label': 'Rows'},
    }
    default_order_by = 'start_time'
    default_order_dir = 'DESC'
    default_view_style = 'row'

    session_key_request_filters = SESSION_KEY_FILTERS
    filters_manager = FiltersManager(SESSION_KEY_FILTERS)

    @property
    def options_order_by(self):
        return [{'value': x, 'label': SORT_OPTIONS[x]['label']} for x in SORT_OPTIONS]

    @property
    def options_order_dir(self):
        return [{'value': x, 'label': self.order_dir[x]['label']} for x in self.order_dir]

    @property
    def options_view_style(self):
        return [{'value': x, 'label': self.view_style[x]['label']} for x in self.view_style]

    def _get_paths(self):
        return Request.objects.values_list('path', flat=True).order_by('path').distinct()

    def _get_views(self):
        return (
            Request.objects.values_list('view_name', flat=True)
            .exclude(view_name='')
            .order_by('view_name')
            .distinct()
        )

    def _get_status_codes(self):
        return (
            Response.objects.values_list('status_code', flat=True)
            .order_by('status_code')
            .distinct()
        )

    def _get_methods(self):
        return Request.objects.values_list('method', flat=True).order_by('method').distinct()

    def _get_sort_list(self, request):
        """Return the current sort list from session, falling back to defaults."""
        if hasattr(request, 'session'):
            return request.session.get(SESSION_KEY_SORT, DEFAULT_SORT_LIST)
        return DEFAULT_SORT_LIST

    def _save_sort_list(self, request, sort_list):
        if hasattr(request, 'session'):
            request.session[SESSION_KEY_SORT] = sort_list

    # Sentinel so we can distinguish "not passed" from explicit None
    _SHOW_NOT_SET = object()

    def _get_objects(self, show=_SHOW_NOT_SET, order_by=None, order_dir=None, path=None, filters=None, sort_list=None, request=None):
        """Build and return a queryset (or sliced queryset for backward compat).

        When *show* is not passed, defaults to self.default_show and slices the
        queryset — preserving the original API so existing tests still pass.
        Pass show=None explicitly to get the full (unsliced) queryset for the paginator.
        """
        if not filters:
            filters = []
        query_set = Request.objects.all()

        # Determine sort
        if sort_list:
            query_set = _apply_sort(query_set, sort_list)
        else:
            if not order_by:
                order_by = self.default_order_by
            if not order_dir:
                order_dir = self.default_order_dir
            if order_by not in SORT_OPTIONS:
                raise RuntimeError('Unknown order_by: "%s"' % order_by)
            query_set = _apply_sort(query_set, [{'field': order_by, 'dir': order_dir}])

        if path:
            query_set = query_set.filter(path=path)
        for f in filters:
            query_set = f.contribute_to_query_set(query_set)
            query_set = query_set.filter(f)

        # Backward-compatible slicing: if show was not explicitly passed, default to default_show
        if show is self._SHOW_NOT_SET:
            show = self.default_show
        if show is not None:
            return query_set[:show]
        return query_set

    def _create_context(self, request):
        raw_filters = self.filters_manager.get(request).copy()
        show = raw_filters.pop('show', self.default_show)
        order_by = raw_filters.pop('order_by', self.default_order_by)
        order_dir = raw_filters.pop('order_dir', self.default_order_dir)
        view_style = raw_filters.pop('view_style', self.default_view_style)

        if show:
            show = int(show)
        per_page = show or DEFAULT_PER_PAGE

        path = request.GET.get('path', None)
        sort_list = self._get_sort_list(request)

        qs = self._get_objects(
            show=None,  # paginator handles limiting
            order_by=order_by,
            order_dir=order_dir,
            path=path,
            filters=[BaseFilter.from_dict(x) for _, x in raw_filters.items()],
            sort_list=sort_list,
        )

        page_obj = get_page(request, qs, per_page)

        # Batch N+1 detection for the current page (1 extra DB query)
        page_request_ids = [r.pk for r in page_obj.object_list]
        has_n1_on_page = False
        if page_request_ids:
            sql_rows = SQLQuery.objects.filter(
                request_id__in=page_request_ids
            ).values('request_id', 'query')
            # Group by request, fingerprint, count occurrences
            buckets = {}  # request_id -> fingerprint -> count
            for row in sql_rows:
                rid = row['request_id']
                fp = fingerprint_query(row['query'])
                buckets.setdefault(rid, {}).setdefault(fp, 0)
                buckets[rid][fp] += 1
            n1_request_ids = {
                rid for rid, fps in buckets.items()
                if any(cnt >= 3 for cnt in fps.values())
            }
            for r in page_obj.object_list:
                r.has_n1 = r.pk in n1_request_ids
            has_n1_on_page = bool(n1_request_ids)

        context = {
            'show': show,
            'per_page': per_page,
            'order_by': order_by,
            'order_dir': order_dir,
            'view_style': view_style,
            'request': request,
            'options_show': self.show,
            'options_order_by': self.options_order_by,
            'options_order_dir': self.options_order_dir,
            'options_view_style': self.options_view_style,
            'options_paths': self._get_paths(),
            'options_status_codes': self._get_status_codes(),
            'options_methods': self._get_methods(),
            'view_names': self._get_views(),
            'filters': raw_filters,
            'sort_list': sort_list,
            'sort_fields_used': [item['field'] for item in sort_list],
            'sort_options': [
                {'value': k, 'label': v['label']} for k, v in SORT_OPTIONS.items()
            ],
            'time_presets': [
                {'key': k, 'seconds': v, 'label': k} for k, v in TIME_RANGE_PRESETS.items()
            ],
            'page_obj': page_obj,
            'results': page_obj.object_list,  # backward compat
            'has_n1_on_page': has_n1_on_page,
        }
        context.update(csrf(request))
        if path:
            context['path'] = path
        return context

    @method_decorator(login_possibly_required)
    @method_decorator(permissions_possibly_required)
    def get(self, request):
        # Read sort_criteria JSON from URL param (enables shared URLs to restore sort state)
        if request.GET.get('sort_criteria'):
            try:
                sort_list = json.loads(request.GET['sort_criteria'])
                if isinstance(sort_list, list) and sort_list:
                    self._save_sort_list(request, sort_list)
            except (ValueError, TypeError):
                pass
        # Handle sort_criteria from GET (backward compat: order_by / order_dir)
        elif request.GET.get('order_by') or request.GET.get('order_dir'):
            ob = request.GET.get('order_by', self.default_order_by)
            od = request.GET.get('order_dir', self.default_order_dir)
            self._save_sort_list(request, [{'field': ob, 'dir': od}])

        if request.GET:
            filters = {
                **self.filters_manager.get(request),
                **{
                    k: v
                    for k, v in request.GET.items()
                    if k in ['show', 'order_by', 'order_dir', 'view_style']
                },
            }
            # per_page in URL is an alias for show (enables shared URLs to restore page size)
            if 'per_page' in request.GET and 'show' not in request.GET:
                filters['show'] = request.GET['per_page']
            # ?view= from N+1 suspects link — save as a proper ViewNameFilter in session
            if request.GET.get('view'):
                from silk.request_filters import ViewNameFilter
                filters['view'] = ViewNameFilter(request.GET['view']).as_dict()
            self.filters_manager.save(request, filters)
        return render(request, 'silk/requests.html', self._create_context(request))

    @method_decorator(login_possibly_required)
    @method_decorator(permissions_possibly_required)
    def post(self, request):
        previous_session = self.filters_manager.get(request)

        # Handle sort_criteria update from POST
        sort_criteria_raw = request.POST.get('sort_criteria', '')
        if sort_criteria_raw:
            try:
                sort_list = json.loads(sort_criteria_raw)
                if isinstance(sort_list, list):
                    self._save_sort_list(
                        request, sort_list if sort_list else DEFAULT_SORT_LIST
                    )
            except (ValueError, TypeError):
                pass

        # Detect whether this POST came from the filter form or the sort/toolbar form.
        # The filter form always includes at least one filter-*-typ hidden field.
        # The sort/toolbar form only contains sort_criteria, show, view_style.
        is_filter_submit = any(k.startswith('filter-') for k in request.POST)

        if 'clear_filters' in request.POST:
            filters = {k: v for k, v in previous_session.items() if k in ['show', 'view_style']}
            self.filters_manager.save(request, filters)
        elif is_filter_submit:
            # Full filter form submitted — replace filter set with what the form says.
            filters = {
                **{k: v for k, v in previous_session.items() if k in ['show', 'order_by', 'order_dir', 'view_style']},
                **{ident: f.as_dict() for ident, f in filters_from_request(request).items()},
            }
            self.filters_manager.save(request, filters)
        else:
            # Sort / toolbar form — only update show/view_style, keep all existing filters.
            non_filter_keys = ['show', 'order_by', 'order_dir', 'view_style']
            updated = {k: v for k, v in request.POST.items() if k in non_filter_keys}
            filters = {**previous_session, **updated}
            self.filters_manager.save(request, filters)

        return render(request, 'silk/requests.html', self._create_context(request))
