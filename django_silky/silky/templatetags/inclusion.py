from django.template import Library


def request_summary(request):
    return {'request': request}


register = Library()

register.inclusion_tag('silky/inclusion/request_summary.html')(request_summary)


def code(lines, actual_line):
    return {'code': lines, 'actual_line': actual_line}


register.inclusion_tag('silky/inclusion/code.html')(code)