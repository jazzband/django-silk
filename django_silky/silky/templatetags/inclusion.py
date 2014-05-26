from django.template import Library

register = Library()


def request_summary(request):
    return {'request': request}

def profile_summary(profile):
    return {'profile': profile}


def code(lines, actual_line):
    return {'code': lines, 'actual_line': actual_line}


register.inclusion_tag('silky/inclusion/request_summary.html')(request_summary)
register.inclusion_tag('silky/inclusion/profile_summary.html')(profile_summary)
register.inclusion_tag('silky/inclusion/code.html')(code)


