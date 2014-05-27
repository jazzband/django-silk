from django.template import Library

register = Library()


def request_summary(silky_request):
    return {'silky_request': silky_request}


def request_menu(request, silky_request):
    return {'request': request,
            'silky_request': silky_request}

def root_menu(request):
    return {'request': request}


def profile_menu(request, profile, silky_request=None):
    context = {'request': request, 'profile': profile}
    if silky_request:
        context['silky_request'] = silky_request
    return context


def profile_summary(profile):
    return {'profile': profile}

def heading(text):
    return {'text': text}


def code(lines, actual_line):
    return {'code': lines, 'actual_line': [x.strip() for x in actual_line]}


register.inclusion_tag('silky/inclusion/request_summary.html')(request_summary)
register.inclusion_tag('silky/inclusion/profile_summary.html')(profile_summary)
register.inclusion_tag('silky/inclusion/code.html')(code)
register.inclusion_tag('silky/inclusion/request_menu.html')(request_menu)
register.inclusion_tag('silky/inclusion/profile_menu.html')(profile_menu)
register.inclusion_tag('silky/inclusion/root_menu.html')(root_menu)
register.inclusion_tag('silky/inclusion/heading.html')(heading)


