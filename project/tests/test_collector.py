import cProfile
import os.path
import sys

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

    def test_configure_exception(self):
        other_profiler = cProfile.Profile()
        other_profiler.enable()
        collector = DataCollector()
        collector.configure()
        other_profiler.disable()
        if sys.version_info >= (3, 12):
            self.assertEqual(collector.local.pythonprofiler, None)
        else:
            self.assertIsNotNone(collector.local.pythonprofiler)
            collector.stop_python_profiler()

    def test_profile_file_name_with_disabled_extended_file_name(self):
        SilkyConfig().SILKY_PYTHON_PROFILER_EXTENDED_FILE_NAME = False
        request_path = "normal/uri/"
        resulting_prefix = self._get_prof_file_name(request_path)
        self.assertEqual(resulting_prefix, "")

    def test_profile_file_name_with_enabled_extended_file_name(self):

        SilkyConfig().SILKY_PYTHON_PROFILER_EXTENDED_FILE_NAME = True
        request_path = "normal/uri/"
        resulting_prefix = self._get_prof_file_name(request_path)
        self.assertEqual(resulting_prefix, "normal_uri_")

    def test_profile_file_name_with_path_traversal_and_special_char(self):
        SilkyConfig().SILKY_PYTHON_PROFILER_EXTENDED_FILE_NAME = True
        request_path = "spÉciàl/.././大/uri/@É/"
        resulting_prefix = self._get_prof_file_name(request_path)
        self.assertEqual(resulting_prefix, "special_uri_e_")

    def test_profile_file_name_with_long_path(self):
        SilkyConfig().SILKY_PYTHON_PROFILER_EXTENDED_FILE_NAME = True
        request_path = "long/path/" + "a" * 100
        resulting_prefix = self._get_prof_file_name(request_path)
        # the path is limited to 50 char plus the last `_`
        self.assertEqual(len(resulting_prefix), 51)

    @classmethod
    def _get_prof_file_name(cls, request_path: str) -> str:
        request = RequestMinFactory()
        request.path = request_path
        DataCollector().configure(request)
        DataCollector().finalise()
        file_path = DataCollector().request.prof_file.name
        filename = os.path.basename(file_path)
        return filename.replace(f"{request.id}.prof", "")
