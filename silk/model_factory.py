import base64
import json
import logging
import re
import sys
import traceback
from uuid import UUID

from django.core.exceptions import RequestDataTooBig
from django.urls import Resolver404, resolve

from silk import models
from silk.collector import DataCollector
from silk.config import SilkyConfig

Logger = logging.getLogger('silk.model_factory')

content_types_json = ['application/json',
                      'application/x-javascript',
                      'text/javascript',
                      'text/x-javascript',
                      'text/x-json']
multipart_form = 'multipart/form-data'
content_type_form = [multipart_form,
                     'application/x-www-form-urlencoded']
content_type_html = ['text/html']
content_type_css = ['text/css']


class DefaultEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, UUID):
            return str(o)


def _parse_content_type(content_type):
    """best efforts on pulling out the content type and encoding from content-type header"""
    char_set = None
    if content_type.strip():
        splt = content_type.split(';')
        content_type = splt[0]
        try:
            raw_char_set = splt[1].strip()
            key, char_set = raw_char_set.split('=')
            if key != 'charset':
                char_set = None
        except (IndexError, ValueError):
            pass
    return content_type, char_set


class RequestModelFactory:
    """Produce Request models from Django request objects"""
    # String to replace on masking
    CLEANSED_SUBSTITUTE = '********************'

    def __init__(self, request):
        super().__init__()
        self.request = request

    def content_type(self):
        content_type = self.request.headers.get('content-type', '')
        return _parse_content_type(content_type)

    def encoded_headers(self):
        """
        From Django docs (https://docs.djangoproject.com/en/2.0/ref/request-response/#httprequest-objects):
        """
        sensitive_headers = set(map(str.lower, SilkyConfig().SILKY_SENSITIVE_KEYS))
        sensitive_headers.add('authorization')
        if SilkyConfig().SILKY_HIDE_COOKIES:
            sensitive_headers.add('cookie')

        headers = {}
        for k, v in self.request.headers.items():
            k = k.lower()
            if k in sensitive_headers:
                v = RequestModelFactory.CLEANSED_SUBSTITUTE
            headers[k] = v

        return json.dumps(headers, cls=DefaultEncoder, ensure_ascii=SilkyConfig().SILKY_JSON_ENSURE_ASCII)

    def _mask_credentials(self, body):
        """
        Mask credentials of potentially sensitive info before saving to db.
        """
        sensitive_keys = SilkyConfig().SILKY_SENSITIVE_KEYS
        key_string = '|'.join(sensitive_keys)

        def replace_pattern_values(obj):
            pattern = re.compile(key_string, re.I)
            if isinstance(obj, dict):
                for key in obj.keys():
                    if pattern.search(key):
                        obj[key] = RequestModelFactory.CLEANSED_SUBSTITUTE
                    else:
                        obj[key] = replace_pattern_values(obj[key])
            elif isinstance(obj, list):
                for index, item in enumerate(obj):
                    obj[index] = replace_pattern_values(item)
            else:
                if pattern.search(str(obj)):
                    return RequestModelFactory.CLEANSED_SUBSTITUTE
            return obj

        try:
            json_body = json.loads(body)
        except Exception as e:
            pattern = re.compile(fr'(({key_string})[^=]*)=(.*?)(&|$)', re.M | re.I)
            try:
                body = re.sub(pattern, f'\\1={RequestModelFactory.CLEANSED_SUBSTITUTE}\\4', body)
            except Exception:
                Logger.debug(f'{str(e)}')
        else:
            body = json.dumps(replace_pattern_values(json_body), ensure_ascii=SilkyConfig().SILKY_JSON_ENSURE_ASCII)

        return body

    def _body(self, raw_body, content_type):
        """
        Encode body as JSON if possible so can be used as a dictionary in generation
        of curl/django test client code
        """
        body = ''
        if content_type in content_type_form:
            body = self.request.POST
            body = json.dumps(dict(body), sort_keys=True, indent=4
                              , ensure_ascii=SilkyConfig().SILKY_JSON_ENSURE_ASCII)
        elif content_type in content_types_json:
            try:
                body = json.dumps(json.loads(raw_body), sort_keys=True, indent=4
                                  , ensure_ascii=SilkyConfig().SILKY_JSON_ENSURE_ASCII)
            except Exception:
                body = raw_body
        return body

    def body(self):
        content_type, char_set = self.content_type()
        if content_type == multipart_form:
            raw_body = b"Raw body not available for multipart_form data, Silk is not showing file uploads."
            body = ''
            return body, raw_body
        try:
            raw_body = self.request.body
        except RequestDataTooBig:
            raw_body = b"Raw body exceeds DATA_UPLOAD_MAX_MEMORY_SIZE, Silk is not showing file uploads."
            body = self.request.POST.copy()
            for k, v in self.request.FILES.items():
                body.appendlist(k, v)
            return body, raw_body
        if char_set:
            try:
                raw_body = raw_body.decode(char_set)
            except AttributeError:
                pass
            except LookupError:  # If no encoding exists, default to UTF-8
                try:
                    raw_body = raw_body.decode('UTF-8')
                except AttributeError:
                    pass
                except UnicodeDecodeError:
                    raw_body = ''
            except Exception as e:
                Logger.error(
                    'Unable to decode request body using char_set %s due to error: %s. Will ignore. Stacktrace:'
                    % (char_set, e)
                )
                traceback.print_exc()
        else:
            # Default to an attempt at UTF-8 decoding.
            try:
                raw_body = raw_body.decode('UTF-8')
            except AttributeError:
                pass
            except UnicodeDecodeError:
                raw_body = ''
        max_size = SilkyConfig().SILKY_MAX_REQUEST_BODY_SIZE
        body = ''
        if raw_body:
            if max_size > -1:
                Logger.debug('A max request size is set so checking size')
                size = sys.getsizeof(raw_body, default=None)
                request_identifier = self.request.path
                if not size:
                    Logger.error(
                        'No way in which to get size of request body for %s, will ignore it',
                        request_identifier
                    )
                elif size <= max_size:
                    Logger.debug(
                        'Request %s has body of size %d which is less than %d so will save the body'
                        % (request_identifier, size, max_size)
                    )
                    body = self._body(raw_body, content_type)
                else:
                    Logger.debug(
                        'Request %s has body of size %d which is greater than %d, therefore ignoring'
                        % (request_identifier, size, max_size)
                    )
                    raw_body = None
            else:
                Logger.debug('No maximum request body size is set, continuing.')
                body = self._body(raw_body, content_type)
        body = self._mask_credentials(body)
        raw_body = self._mask_credentials(raw_body)
        return body, raw_body

    def query_params(self):
        query_params = self.request.GET
        encoded_query_params = ''
        if query_params:
            query_params_dict = dict(zip(query_params.keys(), query_params.values()))
            encoded_query_params = json.dumps(query_params_dict, ensure_ascii=SilkyConfig().SILKY_JSON_ENSURE_ASCII)
        return encoded_query_params

    def view_name(self):
        try:
            resolved = resolve(self.request.path_info)
        except Resolver404:
            return None

        return resolved.view_name

    def construct_request_model(self):
        body, raw_body = self.body()
        query_params = self.query_params()
        path = self.request.path
        view_name = self.view_name()

        request_model = models.Request.objects.create(
            path=path,
            encoded_headers=self.encoded_headers(),
            method=self.request.method,
            query_params=query_params,
            view_name=view_name,
            body=body)
        # Text fields are encoded as UTF-8 in Django and hence will try to coerce
        # anything to we pass to UTF-8. Some stuff like binary will fail.
        try:
            request_model.raw_body = raw_body
        except UnicodeDecodeError:
            Logger.debug('NYI: Binary request bodies')  # TODO
        Logger.debug('Created new request model with pk %s' % request_model.pk)
        return request_model


class ResponseModelFactory:
    """given a response object, craft the silk response model"""

    def __init__(self, response):
        super().__init__()
        self.response = response
        self.request = DataCollector().request

    def body(self):
        body = ''
        content_type, char_set = _parse_content_type(self.response.get('content-type', ''))
        content = getattr(self.response, 'content', '')
        if content:
            max_body_size = SilkyConfig().SILKY_MAX_RESPONSE_BODY_SIZE
            if max_body_size > -1:
                Logger.debug('Max size of response body defined so checking')
                size = sys.getsizeof(content, None)
                if not size:
                    Logger.error('Could not get size of response body. Ignoring')
                    content = ''
                else:
                    if size > max_body_size:
                        content = ''
                        Logger.debug(
                            'Size of %d for %s is bigger than %d so ignoring response body'
                            % (size, self.request.path, max_body_size)
                        )
                    else:
                        Logger.debug(
                            'Size of %d for %s is less than %d so saving response body'
                            % (size, self.request.path, max_body_size)
                        )
            if content and content_type in content_types_json:
                # TODO: Perhaps theres a way to format the JSON without parsing it?
                if not isinstance(content, str):
                    # byte string is not compatible with json.loads(...)
                    # and json.dumps(...) in python3
                    content = content.decode()
                try:
                    body = json.dumps(json.loads(content), sort_keys=True, indent=4
                                      , ensure_ascii=SilkyConfig().SILKY_JSON_ENSURE_ASCII)
                except (TypeError, ValueError):
                    Logger.warn(
                        'Response to request with pk %s has content type %s but was unable to parse it'
                        % (self.request.pk, content_type)
                    )
        return body, content

    def construct_response_model(self):
        assert self.request, 'Cant construct a response model if there is no request model'
        Logger.debug(
            'Creating response model for request model with pk %s'
            % self.request.pk
        )
        b, content = self.body()
        headers = {}
        for k, v in self.response.headers.items():
            try:
                header, val = v
            except ValueError:
                header, val = k, v
            finally:
                headers[header] = val
        silky_response = models.Response(
            request_id=self.request.id,
            status_code=self.response.status_code,
            encoded_headers=json.dumps(headers, ensure_ascii=SilkyConfig().SILKY_JSON_ENSURE_ASCII),
            body=b
        )

        try:
            raw_body = base64.b64encode(content)
        except TypeError:
            raw_body = base64.b64encode(content.encode('utf-8'))
        silky_response.raw_body = raw_body.decode('ascii')
        silky_response.save()
        return silky_response
