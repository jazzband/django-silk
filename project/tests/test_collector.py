from django.test import TestCase
from tests.util import DictStorage

from silk.collector import DataCollector
from silk.config import SilkyConfig

from .factories import RequestMinFactory


class TestCollector(TestCase):
    def test_singleton(self):
        a = DataCollector()
        b = DataCollector()
        c = DataCollector()
        self.assertTrue(a == b == c)

    def test_query_registration(self):
        mock_query = {}
        DataCollector().register_query(mock_query)
        self.assertIn(mock_query, list(DataCollector().queries.values()))

    def test_clear(self):
        self.test_query_registration()
        DataCollector().clear()
        self.assertFalse(DataCollector().queries)

    def test_finalise(self):
        request = RequestMinFactory()
        DataCollector().configure(request)
        with self.subTest("Default file-based storage"):
            DataCollector().finalise()
            file = DataCollector().request.prof_file
            self.assertIsNotNone(file)
            with file.storage.open(file.name) as f:
                content = f.read()
                self.assertTrue(content)

        # Some storages, such as S3Boto3Storage, don't support local file system path.
        # Simulate this behaviour using DictStorage.
        with self.subTest("Pathless storage"):
            request.prof_file.storage = DictStorage()
            DataCollector().finalise()
            file = DataCollector().request.prof_file
            self.assertIsNotNone(file)
            with file.storage.open(file.name) as f:
                content = f.read()
                self.assertTrue(content)
                self.assertGreater(len(content), 0)

    def test_profile_file_name(self):
        request = RequestMinFactory()
        DataCollector().configure(request)
        expected_file_name_prefix = request.path.replace('/', '_').lstrip('_')
        print(expected_file_name_prefix)

        with self.subTest("With disabled extended file name"):
            SilkyConfig().SILKY_PYTHON_PROFILER_EXTENDED_FILE_NAME = False
            DataCollector().finalise()
            file = DataCollector().request.prof_file
            result_file_name = file.name.rsplit('/')[-1]
            self.assertFalse(result_file_name.startswith(f"{expected_file_name_prefix}_"))

        with self.subTest("With enabled extended file name"):
            SilkyConfig().SILKY_PYTHON_PROFILER_EXTENDED_FILE_NAME = True
            DataCollector().finalise()
            file = DataCollector().request.prof_file
            result_file_name = file.name.rsplit('/')[-1]
            self.assertTrue(result_file_name.startswith(f"{expected_file_name_prefix}_"))
