"""Exercise download callbacks and the matching native Shortcuts file routes.

Network downloads and a-Shell processes are stubbed; files and ZIPs are real.
Run with: python3 -m unittest discover -s tests -v
"""
import importlib.util
import json
import os
from pathlib import Path
import plistlib
import tempfile
import types
import unittest
from unittest.mock import MagicMock, patch
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('sw_dlt', ROOT / 'src/SW_DLT.py')
sw = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sw)


class FileReturnTests(unittest.TestCase):
    def test_all_download_callbacks_identify_the_app_and_an_existing_file(self):
        for app in ('a-Shell', 'a-Shell-mini', ''):
            for mode in ('audio', 'video', 'playlist', 'gallery-single', 'gallery-multiple'):
                with self.subTest(app=app, mode=mode), tempfile.TemporaryDirectory() as tmp:
                    previous = Path.cwd()
                    try:
                        os.chdir(tmp)
                        ydl = MagicMock()
                        ydl.__enter__.return_value = ydl
                        ydl.extract_info.return_value = {'title': 'Test media'}
                        def download(_):
                            path = Path('fixture/track.m4a') if mode == 'playlist' else Path('fixture.m4a')
                            path.parent.mkdir(exist_ok=True)
                            path.write_bytes(b'test payload')
                        ydl.download.side_effect = download
                        fake_ytdlp = types.SimpleNamespace(YoutubeDL=MagicMock(return_value=ydl), utils=types.SimpleNamespace(DownloadError=RuntimeError))
                        def gallery_process(*args, **kwargs):
                            for index in range(2 if mode == 'gallery-multiple' else 1):
                                Path(f'fixture/image-{index}.jpg').write_bytes(b'test payload')
                            process = MagicMock()
                            process.__enter__.return_value.stdout = []
                            return process
                        with patch.dict(os.environ, {'APPNAME': app}), patch.object(sw, 'yt_dlp', fake_ytdlp, create=True), patch.object(sw.subprocess, 'Popen', side_effect=gallery_process):
                            args = {'audio': ('-a',), 'video': ('-v', '-d'), 'playlist': ('-p', '-a')}.get(mode, ('-g', '1-2'))
                            result = sw.SW_DLT('fixture', 'https://example.invalid/media', *args).run()
                        callback = urlparse(result)
                        query = parse_qs(callback.query)
                        payload = json.loads(query['text'][0])
                        self.assertEqual((callback.scheme, callback.netloc, query['name']), ('shortcuts', 'run-shortcut', ['SW-DLT']))
                        self.assertEqual(payload['output_code'], 'success')
                        self.assertTrue(Path(payload['file_name']).is_file())
                        self.assertTrue(payload['file_title'])
                        self.assertEqual(payload['app_name'], app)
                    finally:
                        os.chdir(previous)

    def test_shortcut_routes_to_both_app_folders_and_preserves_the_file_output(self):
        workflow = plistlib.loads((ROOT / 'src/SW-DLT.plist').read_bytes())
        actions = workflow['WFWorkflowActions']
        self.assertFalse(any(a['WFWorkflowActionIdentifier'].endswith('.GetFileIntent') for a in actions))
        by_id = {a['WFWorkflowActionParameters']['UUID']: a for a in actions if 'UUID' in a['WFWorkflowActionParameters']}
        native_files = [a['WFWorkflowActionParameters'] for a in actions if a['WFWorkflowActionIdentifier'] == 'is.workflow.actions.documentpicker.open']
        self.assertEqual({a['WFFile']['fileLocation']['appContainerBundleIdentifier'] for a in native_files}, {'AsheKube.app.a-Shell', 'AsheKube.app.a-Shell-mini'})
        for action in native_files:
            folder = action['WFFile']['fileLocation']
            self.assertEqual(folder['relativeSubpath'], 'SW-DLT')
            self.assertNotIn('crossDeviceItemID', action['WFFile'])
            reference = action['WFGetFilePath']['Value']['attachmentsByRange']['{0, 1}']
            last = by_id[reference['OutputUUID']]['WFWorkflowActionParameters']
            self.assertEqual(last['WFItemSpecifier'], 'Last Item')
            split = by_id[last['WFInput']['Value']['OutputUUID']]['WFWorkflowActionParameters']
            self.assertEqual(split['WFTextCustomSeparator'], '/')
        selector = next(a['WFWorkflowActionParameters'] for a in actions if a['WFWorkflowActionIdentifier'] == 'is.workflow.actions.conditional' and a['WFWorkflowActionParameters'].get('WFConditionalActionString') == 'a-Shell')
        app_source = by_id[selector['WFInput']['Variable']['Value']['OutputUUID']]['WFWorkflowActionParameters']
        self.assertEqual(app_source['WFDictionaryKey'], 'app_name')
        start = actions.index(next(a for a in actions if a['WFWorkflowActionParameters'] is selector))
        group = [a for a in actions[start:] if a['WFWorkflowActionParameters'].get('GroupingIdentifier') == selector['GroupingIdentifier']]
        otherwise, end = (actions.index(group[i]) for i in (1, 2))
        for app, section in [('AsheKube.app.a-Shell', actions[start:otherwise]), ('AsheKube.app.a-Shell-mini', actions[otherwise:end])]:
            file_action = next(a['WFWorkflowActionParameters'] for a in section if a['WFWorkflowActionIdentifier'] == 'is.workflow.actions.documentpicker.open')
            self.assertEqual(file_action['WFFile']['fileLocation']['appContainerBundleIdentifier'], app)
            assignment = next(a['WFWorkflowActionParameters'] for a in section if a['WFWorkflowActionIdentifier'] == 'is.workflow.actions.setvariable')
            self.assertEqual(assignment['WFVariableName'], 'mediaFile')
            self.assertEqual(assignment['WFInput']['Value']['OutputUUID'], file_action['UUID'])
        rename = next(a['WFWorkflowActionParameters'] for a in actions if a['WFWorkflowActionIdentifier'] == 'is.workflow.actions.setitemname')
        self.assertEqual(rename['WFInput']['Value'], {'Type': 'Variable', 'VariableName': 'mediaFile'})


if __name__ == '__main__':
    unittest.main()
