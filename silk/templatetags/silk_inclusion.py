from django.template import Library
from silk import config

register = Library()


def request_summary(silk_request):
    return {'silk_request': silk_request}

def request_summary_row(silk_request):
    return {'silk_request': silk_request}

def request_menu(request, silk_request):
    return {'request': request,
            'silk_request': silk_request}


def root_menu(request):
    return {'request': request, 'SILKY_DISTRIBUTION_TAB': config.SilkyConfig().SILKY_DISTRIBUTION_TAB}


def profile_menu(request, profile, silk_request=None):
    context = {'request': request, 'profile': profile}
    if silk_request:
        context['silk_request'] = silk_request
    return context


def profile_summary(profile):
    return {'profile': profile}


def heading(text):
    return {'text': text}


def code(lines, actual_line):
    return {'code': lines, 'actual_line': [x.strip() for x in actual_line]}


def request_filter(options_paths, options_status_codes, options_methods, view_names, filters):
    return {
        'options_paths': options_paths,
        'options_status_codes': options_status_codes,
        'options_methods': options_methods,
        'view_names': view_names,
        'filters': filters
    }


register.inclusion_tag('silk/inclusion/request_summary.html')(request_summary)
register.inclusion_tag('silk/inclusion/request_summary_row.html')(request_summary_row)
register.inclusion_tag('silk/inclusion/profile_summary.html')(profile_summary)
register.inclusion_tag('silk/inclusion/code.html')(code)
register.inclusion_tag('silk/inclusion/request_menu.html')(request_menu)
register.inclusion_tag('silk/inclusion/profile_menu.html')(profile_menu)
register.inclusion_tag('silk/inclusion/root_menu.html')(root_menu)
register.inclusion_tag('silk/inclusion/heading.html')(heading)
register.inclusion_tag('silk/inclusion/request_filter.html')(request_filter)
