from unittest import TestCase
from silk.elasticsearch_interface import ElasticsearchInterface


class TestElasticSearch(TestCase):
    def test_create_request(self):
        e = ElasticsearchInterface()
        e.create_request({'path': '/path/to/somewhere'})

    def test_get_requests(self):
        e = ElasticsearchInterface()
        print(e.get_requests())