from urllib.parse import urlencode

try:
    import autopep8
except ImportError:
    autopep8 = None
from django.template import Context, Template

from silk.profiling.dynamic import is_str_typ

template = """\
from django.test import Client
c = Client()
response = c.{{ lower_case_method }}(path='{{ path }}'{% if data or content_type %},{% else %}){% endif %}{% if data %}
data={{ data }}{% endif %}{% if data and content_type %},{% elif data %}){% endif %}{% if content_type %}
content_type='{{ content_type }}'){% endif %}
"""


def _encode_query_params(query_params):
    try:
        query_params = urlencode(query_params)
    except TypeError:
        pass
    return '?' + query_params


def gen(path, method=None, query_params=None, data=None, content_type=None):
    # generates python code representing a call via django client.
    # useful for use in testing
    method = method.lower()
    t = Template(template)
    context = {
        'path': path,
        'lower_case_method': method,
        'content_type': content_type,
    }
    if method == 'get':
        context['data'] = query_params
    else:
        if query_params:
            query_params = _encode_query_params(query_params)
            path += query_params
        if is_str_typ(data):
            data = "'%s'" % data
        context['data'] = data
        context['query_params'] = query_params
    code = t.render(Context(context, autoescape=False))
    if autopep8:
        # autopep8 is not a hard requirement, so we check if it's available
        # if autopep8 is available, we use it to format the code and do things
        # like remove long lines and improve readability
        code = autopep8.fix_code(
            code,
            options=autopep8.parse_args(['--aggressive', '']),
        )
    return code
