import json
import re

from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.utils.safestring import mark_safe

from silky.middleware import ProfilerMiddleware
from silky.models import Request, SQLQuery, Profile


def _page(request, query_set):
    paginator = Paginator(query_set, 10)
    page_number = request.GET.get('page')
    try:
        page = paginator.page(page_number)
    except PageNotAnInteger:
        page = paginator.page(1)
    except EmptyPage:
        page = paginator.page(paginator.num_pages)
    return page


def _url_for_sql_queries(request, request_id):
    return request.build_absolute_uri(reverse('requests', kwargs={'request_id': request_id}))


def requests(request):
    query_set = Request.objects.all().order_by('-start_time')
    page = _page(request, query_set)
    return render_to_response('silky/requests.html', {
        'requests': page,
        'url': _url_for_sql_queries
    })


def sql(request, request_id):
    query_set = SQLQuery.objects.filter(request_id=request_id).order_by('-start_time')
    page = _page(request, query_set)
    return render_to_response('silky/sql.html', {
        'items': page
    })


def _urlify(str):
    r = re.compile("(?P<src>/.*\.py)\", line (?P<num>[0-9]+).*")
    m = r.search(str)
    n = 1
    while m:
        group = m.groupdict()
        src = group['src']
        num = group['num']
        start = m.start('src')
        end = m.end('src')
        rep = '<a name={name} href="?pos={pos}&file_path={src}&line_num={num}#{name}">{src}</a>'.format(pos=n, src=src, num=num, name='c%d' % n)
        str = str[:start] + rep + str[end:]
        m = r.search(str)
        n += 1
    return str


def sql_detail(request, request_id, sql_id):
    sql_query = SQLQuery.objects.get(pk=sql_id)
    pos = int(request.GET.get('pos', 0))
    file_path = request.GET.get('file_path', '')
    line_num = int(request.GET.get('line_num', 0))
    tb = sql_query.traceback_ln_only
    tb = [mark_safe(x) for x in _urlify(tb).split('\n')]
    context = {
        'sql_query': sql_query,
        'traceback': tb,
        'pos': pos,
        'line_num': line_num,
        'file_path': file_path
    }
    if pos and file_path and line_num:
        actual_line, code = _code(file_path, line_num)
        context['code'] = code
        context['actual_line'] = actual_line
    return render_to_response('silky/sql_detail.html', context)


def _code(file_path, line_num):
    actual_line = ''
    lines = ''
    with open(file_path, 'r') as f:
        r = range(max(0, line_num - 10), line_num + 10)
        for i, line in enumerate(f):
            if i in r:
                lines += line
            if i + 1 == line_num:
                actual_line = line
    code = lines.split('\n')
    return actual_line, code


def _code_context(file_path, line_num):
    actual_line, code = _code(file_path, line_num)
    context = {'code': code, 'file_path': file_path, 'line_num': line_num, 'actual_line': actual_line}
    return context


def source(request):
    file_path = request.GET.get('file_path')
    line_num = int(request.GET.get('line_num'))
    context = _code_context(file_path, line_num)
    return render_to_response('silky/code.html', context)


def request(request, request_id):
    r = Request.objects.get(pk=request_id)
    context = {
        'request': r
    }
    if r.query_params:
        context['query_params'] = json.dumps(json.loads(r.query_params), sort_keys=True, indent=4)
    if r.body:
        if r.content_type:
            content_type = r.content_type.split(';')[0]
            if content_type in ProfilerMiddleware.content_types_json:
                context['body'] = json.dumps(json.loads(r.body), sort_keys=True, indent=4)
            else:
                context['body'] = r.body
    return render_to_response('silky/request.html', context)


def profiling(request, request_id):
    r = Request.objects.get(pk=request_id)
    query_set = Profile.objects.filter(request=r).order_by('-start_time')
    page = _page(request, query_set)
    return render_to_response('silky/profiling.html', {
        'request': r,
        'profiles': page
    })


def profile(request, profile_id):
    profile = Profile.objects.get(pk=profile_id)
    context = {'profile': profile}
    if profile.file_path and profile.line_num:
        context['rendered_code'] = _code_context(profile.file_path, profile.line_num)
    return render_to_response('silky/profile.html', context)


