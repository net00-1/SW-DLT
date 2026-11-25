"""Use the official 0.1.1 package as a fixture; never modify its installation.

uv run --with yt-dlp-apple-webkit-jsi==0.1.1 python -m unittest discover -s tests -v
"""
import hashlib
import os
from importlib.metadata import PackageNotFoundError, distribution
from pathlib import Path
import tempfile
import types
import unittest
from unittest.mock import Mock, patch

from test_file_return import sw


class WebKitInstallTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            provider = distribution('yt-dlp-apple-webkit-jsi')
        except PackageNotFoundError:
            raise unittest.SkipTest('Install yt-dlp-apple-webkit-jsi==0.1.1 for the source fixture')
        cls.original = Path(provider.locate_file('yt_dlp_plugins/webkit_jsi/lib/api.py')).read_bytes()
        if hashlib.sha256(cls.original).hexdigest() != 'b719072669a9193397a7d2ac52457eb1ac8388b68a90f432921d1cc9fcd1fb22':
            raise unittest.SkipTest('Requires the unmodified official 0.1.1 source fixture')

    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.path = Path(temp.name) / 'api.py'
        self.path.write_bytes(self.original)
        self.backup = self.path.with_suffix('.py.sw-dlt-backup')
        self.provider = types.SimpleNamespace(version='0.1.1', locate_file=lambda _: self.path)
        mock = patch('importlib.metadata.distribution', return_value=self.provider)
        mock.start()
        self.addCleanup(mock.stop)

    def test_install_repeat_and_reinstall(self):
        for _ in range(2):
            sw.fix_webkit_navigation()
            self.assertEqual(hashlib.sha256(self.path.read_bytes()).hexdigest(),
                             '92ed60b05f57d74d59251a44e3efda189b369eadb44f846f690b492d01199a11')
            self.assertEqual(self.backup.read_bytes(), self.original)
        self.path.write_bytes(self.original)  # A pip reinstall overwrites the fix.
        sw.fix_webkit_navigation()
        self.assertNotEqual(self.path.read_bytes(), self.original)

    def test_unknown_source_is_not_modified(self):
        self.path.write_bytes(b'custom provider source')
        with self.assertRaisesRegex(RuntimeError, 'Provider differs'):
            sw.fix_webkit_navigation()
        self.assertEqual(self.path.read_bytes(), b'custom provider source')
        self.assertFalse(self.backup.exists())

    def test_unknown_version_is_not_modified(self):
        self.provider.version = '0.2.0'
        sw.fix_webkit_navigation()
        self.assertEqual(self.path.read_bytes(), self.original)
        self.assertFalse(self.backup.exists())

    def test_existing_backup_is_preserved(self):
        self.backup.write_bytes(b'other backup')
        with self.assertRaisesRegex(RuntimeError, 'Existing backup differs'):
            sw.fix_webkit_navigation()
        self.assertEqual(self.path.read_bytes(), self.original)
        self.assertEqual(self.backup.read_bytes(), b'other backup')

    def test_failed_replace_preserves_source_and_removes_temporary_file(self):
        with patch.object(Path, 'replace', side_effect=OSError('write failed')):
            with self.assertRaises(OSError):
                sw.fix_webkit_navigation()
        self.assertEqual(self.path.read_bytes(), self.original)
        self.assertEqual(set(self.path.parent.iterdir()), {self.path, self.backup})

    def test_missing_provider_is_optional(self):
        with patch('importlib.metadata.distribution', side_effect=PackageNotFoundError):
            sw.fix_webkit_navigation()
        self.assertEqual(self.path.read_bytes(), self.original)

    def test_main_updates_then_patches_before_importing_ytdlp(self):
        events = []
        downloader = Mock()
        downloader.update_check.side_effect = lambda: events.append('update')
        downloader.run.side_effect = lambda: events.append('download') or 'success'
        previous = Path.cwd()
        try:
            os.chdir(self.path.parent)
            with patch.object(sw, 'SW_DLT', return_value=downloader), \
                 patch.object(sw, 'fix_webkit_navigation', side_effect=lambda: events.append('patch')), \
                 patch.object(sw, '__import__', side_effect=lambda name: events.append('import') or Mock(), create=True), \
                 patch.object(sw.subprocess, 'run'), \
                 patch.object(sw.sys, 'argv', ['SW_DLT.py', 'https://example.invalid/media', '-a']):
                self.assertEqual(sw.main(), 'success')
        finally:
            os.chdir(previous)
        self.assertEqual(events, ['update', 'patch', 'import', 'download'])
