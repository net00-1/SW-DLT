import unittest
import urllib.parse
import sys
import os

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../src")

from SW_DLT import SW_DLT

class unit_tests(unittest.TestCase):

    def test_default_video(self):
        # Tests the default quality option for video
        url = "https://www.youtube.com/watch?v=LXb3EKWsInQ"
        hash = "SW_DLT_DL_DEFAULT_VIDEO"
        title = urllib.parse.quote("COSTA RICA IN 4K 60fps HDR (ULTRA HD)")

        expect_redirect = "shortcuts://run-shortcut?name=SW-DLT&input=text&text=OUTPUT.{0}.mp4.TITLE.{1}".format(hash, title)

        dl_inst = SW_DLT(url, hash)
        self.assertEqual(dl_inst.single_video("-d", None), expect_redirect)

    def test_default_audio(self):
        # Tests the default quality option for audio
        url = "https://www.youtube.com/watch?v=LXb3EKWsInQ"
        hash = "SW_DLT_DL_DEFAULT_AUDIO"
        title = urllib.parse.quote("COSTA RICA IN 4K 60fps HDR (ULTRA HD)")

        expect_redirect = "shortcuts://run-shortcut?name=SW-DLT&input=text&text=OUTPUT.{0}.m4a.TITLE.{1}".format(hash, title)

        dl_inst = SW_DLT(url, hash)
        self.assertEqual(dl_inst.single_audio(), expect_redirect)

    def test_custom_video(self):
        # Tests a custom quality option for video, resulting in a native format
        url = "https://www.youtube.com/watch?v=LXb3EKWsInQ"
        hash = "SW_DLT_DL_CUSTOM_VIDEO"
        title = urllib.parse.quote("COSTA RICA IN 4K 60fps HDR (ULTRA HD)")

        expect_redirect = "shortcuts://run-shortcut?name=SW-DLT&input=text&text=OUTPUT.{0}.mp4.TITLE.{1}".format(hash, title)

        dl_inst = SW_DLT(url, hash)
        self.assertEqual(dl_inst.single_video("1080", "60"), expect_redirect)

    def test_custom_video_format(self):
        # Tests a custom quality option for video, resulting in non-native format
        url = "https://www.youtube.com/watch?v=LXb3EKWsInQ"
        hash = "SW_DLT_DL_CUSTOM_VIDEO_WEBM"
        title = urllib.parse.quote("COSTA RICA IN 4K 60fps HDR (ULTRA HD)")

        expect_redirect = "shortcuts://run-shortcut?name=SW-DLT&input=text&text=OUTPUT.{0}.webm.TITLE.{1}".format(hash, title)

        dl_inst = SW_DLT(url, hash)
        self.assertEqual(dl_inst.single_video("2160", "60"), expect_redirect)

    def test_video_playlist(self):
        # Tests a playlist download for videos
        url = ""
        hash = "SW_DLT_DL_VIDEO_PLAYLIST"
        title = urllib.parse.quote("SW-DLT Queue")

        expect_redirect = "shortcuts://run-shortcut?name=SW-DLT&input=text&text=OUTPUT.{0}.zip.TITLE.{1}".format(hash, title)

        dl_inst = SW_DLT(url, hash)
        self.assertEqual(dl_inst.playlist_download("-v"), expect_redirect)

    def test_audio_playlist(self):
        # Tests a playlist download for audios
        url = ""
        hash = "SW_DLT_DL_AUDIO_PLAYLIST"
        title = urllib.parse.quote("SW-DLT Queue")

        expect_redirect = "shortcuts://run-shortcut?name=SW-DLT&input=text&text=OUTPUT.{0}.zip.TITLE.{1}".format(hash, title)

        dl_inst = SW_DLT(url, hash)
        self.assertEqual(dl_inst.playlist_download("-a"), expect_redirect)

    def test_dl_error(self):
        # Tests the error redirect for an invalid video
        url = "https://www.youtube.com/watch?v=hftghtrdhdrt" # Invalid video URL
        hash = "ERROR_TEST"

        expect_redirect = "shortcuts://run-shortcut?name=SW-DLT&input=text&text=EXCEPTION.vars.downloadError"

        dl_inst = SW_DLT(url, hash)
        self.assertEqual(dl_inst.single_video("-d", None), expect_redirect)

    def test_gallery_download(self):
        # Tests downloading using gallery-dl
        url = "https://www.instagram.com/microsoft/?hl=en" # Invalid video URL
        hash = "SW_DLT_DL_GALLERY"

        dl_inst = SW_DLT(url, hash)
        expect_redirect = "shortcuts://run-shortcut?name=SW-DLT&input=text&text=OUTPUT.{0}.zip.TITLE.{1}".format(hash, dl_inst.date_id)

        self.assertEqual(dl_inst.gallery_download("1-20", ""), expect_redirect)

        
if __name__ == "__main__":
    unittest.main()