"""Exercise download callbacks and the matching native Shortcuts file routes.

Network downloads and a-Shell processes are stubbed; files and ZIPs are real.
Run with: python3 -m unittest discover -s tests -v
"""
import importlib.util
import json
import os
from pathlib import Path
import plistlib
import re
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

    def test_native_file_routes_preserve_nested_paths_and_return_if_result(self):
        actions = plistlib.loads((ROOT / 'src/SW-DLT.plist').read_bytes())['WFWorkflowActions']
        by_id = {a['WFWorkflowActionParameters']['UUID']: a for a in actions if 'UUID' in a['WFWorkflowActionParameters']}
        self.assertFalse(any(a['WFWorkflowActionIdentifier'].endswith('.GetFileIntent') for a in actions))
        selector = next(a['WFWorkflowActionParameters'] for a in actions if a['WFWorkflowActionParameters'].get('WFConditionalActionString') == 'a-Shell')
        self.assertEqual(selector['WFInput']['Variable']['Value']['Aggrandizements'][0]['DictionaryKey'], 'app_name')
        app_input = by_id[selector['WFInput']['Variable']['Value']['OutputUUID']]
        self.assertEqual(app_input['WFWorkflowActionIdentifier'], 'is.workflow.actions.detect.dictionary')
        start = next(i for i, a in enumerate(actions) if a['WFWorkflowActionParameters'] is selector)
        group = [i for i in range(start, len(actions)) if actions[i]['WFWorkflowActionParameters'].get('GroupingIdentifier') == selector['GroupingIdentifier']]
        otherwise, end = group[1:]
        for app, branch in [('AsheKube.app.a-Shell', actions[start + 1:otherwise]), ('AsheKube.app.a-Shell-mini', actions[otherwise + 1:end])]:
            self.assertEqual(len(branch), 1)  # The selected file is the branch output.
            self.assertEqual(branch[0]['WFWorkflowActionIdentifier'], 'is.workflow.actions.documentpicker.open')
            file = branch[0]['WFWorkflowActionParameters']
            self.assertEqual(file['WFFile']['fileLocation']['appContainerBundleIdentifier'], app)
            self.assertEqual(file['WFFile']['fileLocation']['relativeSubpath'], 'SW-DLT')
            reference = file['WFGetFilePath']['Value']['attachmentsByRange']['{0, 1}']
            transform = by_id[reference['OutputUUID']]['WFWorkflowActionParameters']
            input_id = transform['WFInput']['Value']['attachmentsByRange']['{0, 1}']['OutputUUID']
            self.assertEqual(by_id[input_id]['WFWorkflowActionParameters']['WFDictionaryKey'], 'file_name')
            for relative in ('audio.m4a', 'playlist.zip', 'gallery/nested/ภาพ 1.jpg'):
                absolute = '/private/var/mobile/Containers/Data/Application/ID/Documents/SW-DLT/' + relative
                self.assertEqual(re.sub(transform['WFReplaceTextFind'], transform['WFReplaceTextReplace'], absolute), relative)
        rename = next(a['WFWorkflowActionParameters'] for a in actions if a['WFWorkflowActionIdentifier'] == 'is.workflow.actions.setitemname')
        self.assertEqual(rename['WFInput']['Value']['OutputUUID'], actions[end]['WFWorkflowActionParameters']['UUID'])


if __name__ == '__main__':
    unittest.main()
