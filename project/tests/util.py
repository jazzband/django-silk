import json
import multiprocessing
import random
from mock import Mock
from silk.utils.six import b

# noinspection PyUnresolvedReferences
from silk.utils.six.moves.BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
# noinspection PyUnresolvedReferences

from silk.utils.six.moves.urllib.parse import urlparse, parse_qs
from silk.models import Request

PORT = random.randint(8000, 9000)
try:  # Py3
    context = getattr(multiprocessing, 'context')
    Process = context.Process
except AttributeError:  # Py2
    Process = getattr(multiprocessing, 'Process')


def delete_all_models(model_class):
    """
    A sqlite3-safe deletion function to avoid "django.db.utils.OperationalError: too many SQL variables"

    :param model_class:
    :return:
    """
    while model_class.objects.count():
        ids = model_class.objects.values_list('pk', flat=True)[:80]
        model_class.objects.filter(pk__in=ids).delete()


def construct_echo_process():
    return Process(target=run_echo_server)


def run_echo_server():
    class Handler(BaseHTTPRequestHandler):
        def _do(self):
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            parsed = urlparse(self.path)
            query_parameters = parse_qs(parsed.query)
            response = {
                'path': parsed.path,
                'headers': dict(self.headers)
            }
            if query_parameters:
                response['query_params'] = query_parameters
            try:
                try:  # py2
                    raw_content_len = self.headers.getheader('content-length')
                except AttributeError:  # py3
                    raw_content_len = self.headers.get('content-length')
                content_len = int(raw_content_len)
            except TypeError:
                content_len = 0
            if content_len:
                body = self.rfile.read(content_len)
                try:  # py3
                    body = body.decode('UTF-8')
                except AttributeError:  # py2
                    pass
                if body:
                    response['body'] = body
            print(response)
            encoded_json = json.dumps(response)
            self.wfile.write(b(encoded_json))
            return

        do_GET = _do
        do_POST = _do
        do_PUT = _do
        do_HEAD = _do
        do_PATCH = _do
        do_OPTIONS = _do
        do_DELETE = _do
        do_TRACE = _do
        do_CONNECT = _do

    server_address = ('', PORT)
    httpd = HTTPServer(server_address, Handler)
    httpd.serve_forever()


def mock_data_collector():
    mock = Mock()
    mock.queries = []
    mock.local = Mock()
    r = Request()
    mock.local.request = r
    mock.request = r
    return mock