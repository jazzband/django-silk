from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator

__author__ = 'mtford'


def _page(request, query_set):
    per_page = request.GET.get('per_page', 200)
    paginator = Paginator(query_set, per_page)
    page_number = request.GET.get('page')
    try:
        page = paginator.page(page_number)
    except PageNotAnInteger:
        page = paginator.page(1)
    except EmptyPage:
        page = paginator.page(paginator.num_pages)
    return page
