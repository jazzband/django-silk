import re

from django.template import Library
from django.template.defaultfilters import stringfilter
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe


register = Library()


def _esc_func(autoescape):
    if autoescape:
        esc = conditional_escape
    else:
        esc = lambda x: x
    return esc


@stringfilter
def spacify(value, autoescape=None):
    esc = _esc_func(autoescape)
    val = esc(value).replace(' ', "&nbsp;")
    val = val.replace('\t', '    ')
    return mark_safe(val)


def _urlify(str):
    r = re.compile("(?P<src>/.*\.py)\", line (?P<num>[0-9]+).*")
    m = r.search(str)
    while m:
        group = m.groupdict()
        src = group['src']
        num = group['num']
        start = m.start('src')
        end = m.end('src')
        rep = '<a href="/silk/src/?file_path={src}&line_num={num}">{src}</a>'.format(src=src, num=num)
        str = str[:start] + rep + str[end:]
        m = r.search(str)
    return str


@stringfilter
def filepath_urlify(value, autoescape=None):
    value = _urlify(value)
    return mark_safe(value)


@stringfilter
def body_filter(value):
    print(value)
    if len(value) > 20:
        return 'Too big!'
    else:
        return value


spacify.needs_autoescape = True
filepath_urlify.needs_autoescape = True
register.filter(spacify)
register.filter(filepath_urlify)
register.filter(body_filter)