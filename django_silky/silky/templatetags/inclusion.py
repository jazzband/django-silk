from django.template import Library

register = Library()


def request_summary(request):
    return {'request': request}


def request_menu(request, silky_request):
    return {'request': request,
            'r': silky_request}


def profile_menu(request, profile):
    return {'request': request,
            'profile': profile}


def profile_summary(profile):
    return {'profile': profile}


def code(lines, actual_line):
    return {'code': lines, 'actual_line': actual_line}


register.inclusion_tag('silky/inclusion/request_summary.html')(request_summary)
register.inclusion_tag('silky/inclusion/profile_summary.html')(profile_summary)
register.inclusion_tag('silky/inclusion/code.html')(code)
register.inclusion_tag('silky/inclusion/request_menu.html')(request_menu)
register.inclusion_tag('silky/inclusion/profile_menu.html')(profile_menu)


