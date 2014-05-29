"""
Test curl command generation by executing the generated command
against a HTTP server that echos various components in the request.
"""

import json
import random
import unittest
import subprocess
import multiprocessing
from six import b, u

PORT = random.randint(8000, 9000)
try:  # Py3
    context = getattr(multiprocessing, 'context')
    Process = context.Process
except AttributeError:  # Py2
    Process = getattr(multiprocessing, 'Process')
# noinspection PyUnresolvedReferences
from six.moves.BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
# noinspection PyUnresolvedReferences
from six.moves.urllib.parse import urlparse, parse_qs
from silky.code_generation.curl import curl_cmd


def run():
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
                try:  #py2
                    raw_content_len = self.headers.getheader('content-length')
                except AttributeError:  #py3
                    raw_content_len = self.headers.get('content-length')
                content_len = int(raw_content_len)
            except TypeError:
                content_len = 0
            if content_len:
                body = self.rfile.read(content_len)
                try:  #py3
                    body = body.decode('UTF-8')
                except AttributeError:  #py2
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


class TestCodeGenerationCurl(unittest.TestCase):
    httpd_process = Process(target=run)
    methods = ['GET', 'POST', 'HEAD', 'PUT', 'PATCH', 'OPTIONS', 'DELETE', 'TRACE', 'CONNECT']

    @classmethod
    def setUpClass(cls):
        cls.httpd_process.start()

    @classmethod
    def tearDownClass(cls):
        cls.httpd_process.terminate()

    def _execute(self, path, method, query_params=None, body=None, content_type=None):
        cmd = curl_cmd('127.0.0.1:%d' % PORT + path, method=method, query_params=query_params, body=body,
                       content_type=content_type)
        print(cmd)
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        stdout, _ = p.communicate()
        if hasattr(stdout, 'decode'):  #py3
            raw_response = stdout.decode("utf-8")
        else:  #py2
            raw_response = stdout
        return json.loads(raw_response)

    def test_query_params(self):
        def _execute_test(method):
            response = self._execute('/', method, {'blah': 5})
            self.assertDictContainsSubset({
                u'path': u'/',
                u'query_params': {
                    u'blah': ['5']
                }
            }, response)

        map(_execute_test, self.methods)

    def test_methods(self):
        def _test_method(method):
            response = self._execute('/', method)
            self.assertDictContainsSubset({u'path': u'/'}, response)
        map(_test_method, self.methods)

    def test_json_body(self):
        def _test_json_body(method):
            body = {
                'x': 5,
                'fdf': 10
            }
            response = self._execute('/', method, body=body, content_type='application/json')
            self.assertDictContainsSubset({
                u'path': u'/',
                u'body': json.dumps(body)
            }, response)
        map(_test_json_body, self.methods)

    def test_raw_json_body(self):
        def _test_json_body(method):
            body = {
                'x': 5,
                'fdf': 10
            }
            response = self._execute('/', method, body=json.dumps(body), content_type='application/json')
            self.assertDictContainsSubset({
                u'path': u'/',
                u'body': json.dumps(body)
            }, response)
        map(_test_json_body, self.methods)

    def test_body_no_content_type(self):
        """should reduce anything with no content_type down to a string"""
        def _test(method):
            body = {"random": "body"}
            response = self._execute('/', method, body=json.dumps(body), content_type='application/json')
            self.assertDictContainsSubset({
                u'path': u'/'
            }, response)
            response_body = response.get('body')
            self.assertDictEqual(body, eval(response_body))
            print(body)
        map(_test, self.methods)

    def test_multipart(self):
        body = {"multi": "part"}
        response = self._execute('/', 'POST', body=body, content_type='multipart/form-data')
        try:
            body = response['body']
        except KeyError:
            self.fail('Response isnt dict')
        self.assertIn('form-data', body)
        self.assertIn('------', body)
        self.assertIn('part', body)
        self.assertIn('multi', body)
        print(response)