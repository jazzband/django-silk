import json
import urllib

import jinja2


curl_template = """
curl {% if method %}-X {{ method }}{% endif %}
{% if content_type %}-H 'Content-Type: {{ content_type }}'{% endif %}
{% if modifier %}{{ modifier }} {% endif %}{% if body %}'{{ body }}'{% endif %}
{{ url }}{% if query_params %}{{ query_params }}{% endif %}
"""


def _curl_process_params(body, content_type, query_params):
    if query_params:
        try:
            query_params = urllib.urlencode(query_params)
        except TypeError:
            pass
        query_params = '?' + str(query_params)
    if 'json' in content_type or 'javascript' in content_type:
        if isinstance(body, dict):
            body = json.dumps(body)
        modifier = '-d'
    elif 'multipart' in content_type:
        body = ' '.join(['%s=%s' % (k, v) for k, v in body.items()])
        content_type = None
        modifier = '-F'
    elif body:
        body = str(body)
        modifier = '-d'
    else:
        modifier = None
        content_type = None
    return modifier, body, query_params, content_type


def curl_cmd(url, method=None, query_params=None, body=None, content_type=None):
    if not content_type:
        content_type = 'text/plain'
    modifier, body, query_params, content_type = _curl_process_params(body, content_type, query_params)
    t = jinja2.Template(curl_template)
    return ' '.join(t.render(url=url,
                             method=method,
                             query_params=query_params,
                             body=body,
                             modifier=modifier,
                             content_type=content_type).split('\n'))

