# This testing template should only be run within the a-Shell app to avoid unexpected behavior
# It is assumed the target SW_DLT source is located in the same directory as the testing suite

import importlib.util
import urllib.parse
import subprocess
import unittest
import json

from SW_DLT_TARGET import SW_DLT

class TestSWDLT(unittest.TestCase):
    
    # @unittest.skip
    def test_default_video(self):
        # Tests downloading a video at the default quality
        url = ""
        hash = "SW_DLT_DL_DEFAULT_VIDEO_TEST"
        
        expected_output = {
            "output_code": "success",
            "file_name": f'{hash}.mp4',
            "file_title": ""
        }
        
        expected_redirect = f'shortcuts://run-shortcut?name=SW-DLT&input=text&text={urllib.parse.quote(json.dumps(expected_output))}'
        
        dv_inst = SW_DLT(url, hash)
        self.assertEqual(dv_inst.single_video("-d", None), expected_redirect)

        
    # @unittest.skip
    def test_default_audio(self):
        # Tests downloading an audio at the default quality
        url = ""
        hash = "SW_DLT_DL_DEFAULT_AUDIO_TEST"
        
        expected_output = {
            "output_code": "success",
            "file_name": f'{hash}.m4a',
            "file_title": ""
        }
        
        expected_redirect = f'shortcuts://run-shortcut?name=SW-DLT&input=text&text={urllib.parse.quote(json.dumps(expected_output))}'
        
        da_inst = SW_DLT(url, hash)
        self.assertEqual(da_inst.single_audio(), expected_redirect)
        
    # @unittest.skip
    def test_custom_video(self):
        # Tests downloading a video with custom framerate and resolution
        url = ""
        hash = "SW_DLT_DL_CUSTOM_VIDEO_NATIVE_TEST"
        
        expected_output = {
            "output_code": "success",
            "file_name": f'{hash}.mp4',
            "file_title": ""
        }
        
        expected_redirect = f'shortcuts://run-shortcut?name=SW-DLT&input=text&text={urllib.parse.quote(json.dumps(expected_output))}'
        
        cvn_inst = SW_DLT(url, hash)
        self.assertEqual(cvn_inst.single_video("1080", "60"), expected_redirect)
        
    # @unittest.skip
    def test_custom_video_maxq(self):
        # Tests downloading a video with the maximum framerate and resolution supported
        url = ""
        hash = "SW_DLT_DL_CUSTOM_VIDEO_MAXQ_TEST"
        
        expected_output = {
            "output_code": "success",
            "file_name": f'{hash}.mp4',
            "file_title": ""
        }
        
        expected_redirect = f'shortcuts://run-shortcut?name=SW-DLT&input=text&text={urllib.parse.quote(json.dumps(expected_output))}'
        
        cvmq_inst = SW_DLT(url, hash)
        self.assertEqual(cvmq_inst.single_video("2160", "60"), expected_redirect)
        
    # @unittest.skip
    def test_video_playlist(self):
        # Tests downloading a video playlist
        url = ""
        hash = "SW_DLT_DL_VIDEO_PLAYLIST_TEST"
        
        expected_output = {
            "output_code": "success",
            "file_name": f'{hash}.zip',
            "file_title": ""
        }
        
        expected_redirect = f'shortcuts://run-shortcut?name=SW-DLT&input=text&text={urllib.parse.quote(json.dumps(expected_output))}'
        
        vp_inst = SW_DLT(url, hash)
        self.assertEqual(vp_inst.playlist_download("-v"), expected_redirect)
    
    # @unittest.skip
    def test_audio_playlist(self):
        # Tests downloading an audio playlist
        url = ""
        hash = "SW_DLT_DL_AUDIO_PLAYLIST_TEST"
        
        expected_output = {
            "output_code": "success",
            "file_name": f'{hash}.zip',
            "file_title": ""
        }
        
        expected_redirect = f'shortcuts://run-shortcut?name=SW-DLT&input=text&text={urllib.parse.quote(json.dumps(expected_output))}'
        
        ap_inst = SW_DLT(url, hash)
        self.assertEqual(ap_inst.playlist_download("-a"), expected_redirect)
        
    # @unittest.skip
    def test_default_gallery(self):
        # Tests downloading a gallery at default settings (all items)
        url = ""
        hash = "SW_DLT_DL_DEFAULT_GALLERY_TEST"
        
        expected_output = {
            "output_code": "success",
            "file_name": f'{hash}.zip',
            "file_title": "DGT_DATE_TITLE"
        }
        
        expected_redirect = f'shortcuts://run-shortcut?name=SW-DLT&input=text&text={urllib.parse.quote(json.dumps(expected_output))}'
        
        dg_inst = SW_DLT(url, hash)
        dg_inst.date_id = "DGT_DATE_TITLE"
        self.assertEqual(dg_inst.gallery_download("-d", ""), expected_redirect)
    
    # @unittest.skip
    def test_custom_gallery(self):
        # Tests downloading a gallery with custom settings (custom range)
        url = ""
        hash = "SW_DLT_DL_CUSTOM_GALLERY_TEST"
        
        expected_output = {
            "output_code": "success",
            "file_name": f'{hash}.jpg',
            "file_title": "CGT_DATE_TITLE"
        }
        
        expected_redirect = f'shortcuts://run-shortcut?name=SW-DLT&input=text&text={urllib.parse.quote(json.dumps(expected_output))}'
        
        cg_inst = SW_DLT(url, hash)
        cg_inst.date_id = "CGT_DATE_TITLE"
        self.assertEqual(cg_inst.gallery_download("3", ""), expected_redirect)

    # @unittest.skip
    def test_ytdlp_error(self):
        # Tests error handling on a yt-dlp download
        url = ""
        hash = "SW_DLT_DL_YTDLP_ERROR_TEST"
        
        expected_output = {
            "output_code": "exception",
            "exc_path": "vars.downloadError"
        }

        exc_msg = f'shortcuts\:\/\/run\-shortcut\?name\=SW\-DLT\&input\=text\&text\={urllib.parse.quote(json.dumps(expected_output))}'
        
        dv_inst = SW_DLT(url, hash)
        with self.assertRaisesRegex(Exception, exc_msg):
            dv_inst.single_video("-d", None)

    # @unittest.skip
    def test_gallery_error(self):
        # Tests error handling on a gallery-dl download
        url = ""
        hash = "SW_DLT_DL_GALLERY_ERROR_TEST"
        
        expected_output = {
            "output_code": "exception",
            "exc_path": "vars.downloadError"
        }

        exc_msg = f'shortcuts\:\/\/run\-shortcut\?name\=SW\-DLT\&input\=text\&text\={urllib.parse.quote(json.dumps(expected_output))}'        
        
        ge_inst = SW_DLT(url, hash)
        ge_inst.date_id = "DGT_DATE_TITLE"
        with self.assertRaisesRegex(Exception, exc_msg):
            ge_inst.gallery_download("-d", "")

    # @unittest.skip
    def test_playlist_error(self):
        # Tests error handling on a yt-dlp playlist download
        url = ""
        hash = "SW_DLT_DL_PLAYLIST_ERROR_TEST"

        expected_output = {
            "output_code": "exception",
            "exc_path": "vars.downloadError"
        }

        exc_msg = f'shortcuts\:\/\/run\-shortcut\?name\=SW\-DLT\&input\=text\&text\={urllib.parse.quote(json.dumps(expected_output))}'
        
        ge_inst = SW_DLT(url, hash)
        with self.assertRaisesRegex(Exception, exc_msg):
            ge_inst.playlist_download("-v")

    # @unittest.skip
    def z_test_missing_dependencies(self):
        # Tests installation of dependencies
        url = "https://url.placeholder.com"
        hash = "SW_DLT_MISSING_DEPS_ERROR_TEST"

        subprocess.run("pip uninstall -y yt-dlp")
        subprocess.run("pip uninstall -y gallery-dl")
        expected_output = {
            "output_code": "exception",
            "exc_path": "vars.restartRequired"
        }

        exc_msg = f'shortcuts\:\/\/run\-shortcut\?name\=SW\-DLT\&input\=text\&text\={urllib.parse.quote(json.dumps(expected_output))}'
        
        md_inst = SW_DLT(url, hash)
        with self.subTest():
            with self.assertRaisesRegex(Exception, exc_msg):
                md_inst.validate_install()
        with self.subTest():
            self.assertEqual(True, importlib.util.find_spec("gallery_dl") is not None)
        with self.subTest():
            self.assertEqual(True, importlib.util.find_spec("yt_dlp") is not None)

    @classmethod
    def tearDownClass(cls):
        subprocess.run("rm -rf SW_DLT*")
            
if __name__ == "__main__":
    unittest.main()
