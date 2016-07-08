"""
Test curl command generation by executing the generated command
against a HTTP server that echos various components in the request.
"""

import json
import unittest
import subprocess

# .util has disappeared so let's comment out the import for
# now since nothing is using it and it's breaking the build
# from .util import PORT, construct_echo_process


# noinspection PyUnresolvedReferences
from silk.code_generation.curl import curl_cmd


# class TestCodeGenerationCurl(unittest.TestCase):
#     httpd_process = construct_echo_process()
#     methods = ['GET', 'POST', 'HEAD', 'PUT', 'PATCH', 'OPTIONS', 'DELETE', 'TRACE', 'CONNECT']
#
#     @classmethod
#     def setUpClass(cls):
#         cls.httpd_process.start()
#
#     @classmethod
#     def tearDownClass(cls):
#         cls.httpd_process.terminate()
#
#     def _execute(self, path, method, query_params=None, body=None, content_type=None):
#         cmd = curl_cmd('127.0.0.1:%d' % PORT + path, method=method, query_params=query_params, body=body,
#                        content_type=content_type)
#         print(cmd)
#         p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
#         stdout, _ = p.communicate()
#         if hasattr(stdout, 'decode'):  #py3
#             raw_response = stdout.decode("utf-8")
#         else:  #py2
#             raw_response = stdout
#         return json.loads(raw_response)
#
#     def test_query_params(self):
#         def _execute_test(method):
#             response = self._execute('/', method, {'blah': 5})
#             self.assertDictContainsSubset({
#                 'path': '/',
#                 'query_params': {
#                     'blah': ['5']
#                 }
#             }, response)
#
#         map(_execute_test, self.methods)
#
#     def test_methods(self):
#         def _test_method(method):
#             response = self._execute('/', method)
#             self.assertDictContainsSubset({'path': '/'}, response)
#         map(_test_method, self.methods)
#
#     def test_json_body(self):
#         def _test_json_body(method):
#             body = {
#                 'x': 5,
#                 'fdf': 10
#             }
#             response = self._execute('/', method, body=body, content_type='application/json')
#             self.assertDictContainsSubset({
#                 'path': '/',
#                 'body': json.dumps(body)
#             }, response)
#         map(_test_json_body, self.methods)
#
#     def test_raw_json_body(self):
#         def _test_json_body(method):
#             body = {
#                 'x': 5,
#                 'fdf': 10
#             }
#             response = self._execute('/', method, body=json.dumps(body), content_type='application/json')
#             self.assertDictContainsSubset({
#                 'path': '/',
#                 'body': json.dumps(body)
#             }, response)
#         map(_test_json_body, self.methods)
#
#     def test_body_no_content_type(self):
#         """should reduce anything with no content_type down to a string"""
#         def _test(method):
#             body = {"random": "body"}
#             response = self._execute('/', method, body=json.dumps(body), content_type='application/json')
#             self.assertDictContainsSubset({
#                 'path': '/'
#             }, response)
#             response_body = response.get('body')
#             self.assertDictEqual(body, eval(response_body))
#             print(body)
#         map(_test, self.methods)
#
#     def test_multipart(self):
#         body = {"multi": "part"}
#         response = self._execute('/', 'POST', body=body, content_type='multipart/form-data')
#         try:
#             body = response['body']
#         except KeyError:
#             self.fail('Response isnt dict')
#         self.assertIn('form-data', body)
#         self.assertIn('------', body)
#         self.assertIn('part', body)
#         self.assertIn('multi', body)
#         print(response)
#
#     def test_form_urlencoded(self):
#         body = {"multi": "part"}
#         response = self._execute('/', 'POST', body=body, content_type='application/x-www-form-urlencoded')
#         try:
#             body = response['body']
#         except KeyError:
#             self.fail('Response isnt dict')
#         print(response)
