import unittest
import urllib.parse
import sys
import os

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../src")

from SW_DLT import SW_DLT

class unit_tests(unittest.TestCase):

    def test_defaultvid(self):
        url = "https://www.youtube.com/watch?v=jflXUguoKtU"
        hash = "SW_DLT_DL_TESTVIDEOHASH"
        title = urllib.parse.quote("Dog Stops Tornado from Forming")

        expect_redirect = "shortcuts://run-shortcut?name=SW-DLT&input=text&text=OUTPUT.{0}.mp4.TITLE.{1}".format(hash, title)

        dl_inst = SW_DLT(url, hash)
        self.assertEqual(dl_inst.single_video("-d", None), expect_redirect)

        
if __name__ == "__main__":
    unittest.main()