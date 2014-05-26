"""
Test curl command generation by executing the generated command
against a HTTP server that echos various components in the request.
"""

import json
import unittest
import subprocess
from multiprocessing import Process
# noinspection PyUnresolvedReferences
from six.moves.BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from urlparse import urlparse, parse_qs
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
                content_len = int(self.headers.getheader('content-length'))
            except TypeError:
                content_len = 0
            if content_len:
                body = self.rfile.read(content_len)
                if body:
                    response['body'] = body
            json.dump(response, self.wfile)
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

    server_address = ('', 8888)
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
        cmd = curl_cmd('127.0.0.1:8888' + path, method=method, query_params=query_params, body=body,
                       content_type=content_type)
        print cmd
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        stdout, _ = p.communicate()
        try:
            response = json.loads(stdout)
        except ValueError:
            response = stdout
        return response

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
            print body
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
        print response