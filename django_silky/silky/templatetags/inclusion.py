from django.template import Library


def request_summary(request):
    return {'request': request}

register = Library()

register.inclusion_tag('silky/request_summary.html')(request_summary)