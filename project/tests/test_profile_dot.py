# std
import cProfile
import os
import tempfile
from contextlib import contextmanager
from unittest.mock import MagicMock

# 3rd party
from django.test import TestCase
from networkx.drawing.nx_pydot import read_dot

# silk
from silk.views.profile_dot import (
    _create_dot,
    _create_profile,
    _temp_file_from_file_field,
)


class ProfileDotViewTestCase(TestCase):

    @classmethod
    @contextmanager
    def _stats_file(cls):
        """
        Context manager to create some arbitrary profiling stats in a temp file, returning the filename on enter,
        and removing the temp file on exit.
        """
        try:
            with tempfile.NamedTemporaryFile(delete=False) as stats:
                pass
            cProfile.run('1+1', stats.name)
            yield stats.name
        finally:
            os.unlink(stats.name)

    @classmethod
    @contextmanager
    def _stats_data(cls):
        """
        Context manager to create some arbitrary profiling stats in a temp file, returning the data on enter,
        and removing the temp file on exit.
        """
        with cls._stats_file() as filename:
            with open(filename, 'rb') as f:
                yield f.read()

    @classmethod
    def _profile(cls):
        """Create some arbitrary profiling stats."""
        with cls._stats_file() as filename:
            # create profile - we don't need to convert a django file field to a temp file
            # just use the filename of the temp file already created
            @contextmanager
            def dummy(_): yield filename
            return _create_profile(filename, dummy)

    @classmethod
    def _mock_file(cls, data):
        """
        Get a mock object that looks like a file but returns data when read is called.
        """
        i = [0]
        def read(n):
            if not i[0]:
                i[0] += 1
                return data

        stream = MagicMock()
        stream.open = lambda: None
        stream.read = read

        return stream

    def test_create_dot(self):
        """
        Verify that a dot file is correctly created from pstats data stored in a file field.
        """
        with self._stats_file() as filename:  # noqa: F841

            try:
                # create dot
                with tempfile.NamedTemporaryFile(delete=False) as dotfile:
                    dot = _create_dot(self._profile(), 5)
                    dotfile.write(dot.encode('utf-8'))

                # verify generated dot is valid
                G = read_dot(dotfile.name)
                self.assertGreater(len(G.nodes()), 0)

            finally:
                os.unlink(dotfile.name)

    def test_temp_file_from_file_field(self):
        """
        Verify that data held in a file like object is copied to a temp file.
        """
        dummy_data = 'dummy data'.encode('utf-8')
        stream = self._mock_file(dummy_data)

        with _temp_file_from_file_field(stream) as filename:
            with open(filename, 'rb') as f:
                self.assertEqual(f.read(), dummy_data)

        # file should have been removed on exit
        self.assertFalse(os.path.exists(filename))
