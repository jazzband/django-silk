import json
import urllib

import jinja2


curl_template = """
curl -i {% if method %}-X {{ method }}{% endif %}
{% if content_type %}-H 'Content-Type: {{ content_type }}'{% endif %}
{% if body %}-d '{{ body }}'{% endif %}
{{ url }}{% if query_params %}{{ query_params }}{% endif %}
"""

httpie_template = """
httpie {{ url }}
{% if method %}{{ method }}{% endif %}
{% if content_type %}Content-Type:{{ content_type }}{% endif %}
{% if body %}{{ body }}{% endif %}
{% if query_params %}{{ query_params }}{% endif %}
"""


def _curl_process_params(body, content_type, query_params):
    if query_params:
        try:
            query_params = urllib.urlencode(query_params)
        except TypeError:
            pass
        query_params = '?' + query_params
    if 'json' in content_type or 'javascript' in content_type:
        try:
            body = json.dumps(body)
        except ValueError:
            pass
    return body, query_params


def curl_cmd(url, method=None, query_params=None, body=None, content_type=None):
    body, query_params = _curl_process_params(body, content_type, query_params)
    t = jinja2.Template(curl_template)
    return ' '.join(t.render(url=url,
                             method=method,
                             query_params=query_params,
                             body=body,
                             content_type=content_type).split('\n'))






if __name__ == '__main__':
    print curl_cmd(url='http://google.com', method='GET', query_params={'x': 2}, body={'blah': 5},
                   content_type='application/json')