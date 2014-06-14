import json
import rawes

ELASTIC_SEARCH_MAPPINGS = {
    'Request': {
        '_all': {
            'enabled': True
        },
        'properties': {
            'path': {},
            'query_params': {},
            'raw_request_body': {},
            'request_body': {},
            'raw_response_body': {},
            'response_body': {},
            'method': {},
            'start_time': {},
            'view_name': {},
            'end_time': {},
            'time_taken': {},
            'request_encoded_headers': {},
            'response_encoded_headers': {},
            'meta_time': {},
            'meta_num_queries': {},
            'meta_time_spent_queries': {},
            'status_code': {},
            'queries': {},
            'profiles': {}
        }
    },
    'Query': {
        '_all': {
            'enabled': True
        },
        'properties': {
            'query': {},
            'start_time': {},
            'end_time': {},
            'time_taken': {},
            'request': {},
            'traceback': {}
        }
    },
    'Profile': {
        '_all': {
            'enabled': True
        },
        'properties': {
            'name': {},
            'start_time': {},
            'end_time': {},
            'request': {},
            'time_taken': {},
            'file_path': {},
            'line_num': {},
            'end_line_num': {},
            'func_name': {},
            'exception_raised': {},
            'queries': {},
            'dynamic': {}
        }
    }
}

ELASTIC_SEARCH_SETTINGS = {}


class ElasticsearchInterface(object):
    host = 'localhost'
    port = 9202

    def __init__(self):
        super(ElasticsearchInterface, self).__init__()
        self.es = rawes.Elastic('%s:%d' % (self.host, self.port))

    def create_request(self, data):
        self.es.post('silk/requests', data=data)

    def get_requests(self):
        query = {
            'query': {
                'match_all': {}
            }
        }
        r = self.es.get('silk/requests/_search', data=json.dumps(query))
        hits = r['hits']
        total = hits['total']
        results = []
        for hit in hits['hits']:
            processed = {
                'id': hit['_id']
            }
            processed.update(hit['_source'])
            results.append(processed)
        return results, total