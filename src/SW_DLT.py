# SW-DLT script, do not copy without permission!

import urllib.parse
import subprocess
import mimetypes
import datetime
import shutil
import sys
import re
import os

try:
    import requests
    import youtube_dl

except:
    pass


class SWDLT:
    FFMPEG_URL = "https://github.com/holzschu/a-Shell-commands/releases/download/0.1/ffmpeg.wasm"
    FFPROBE_URL = "https://github.com/holzschu/a-Shell-commands/releases/download/0.1/ffprobe.wasm"
    REBOOT_EXC = "open shortcuts://run-shortcut?name=SW-DLT&input=text&text=EXCEPTION.vars.restartRequired"
    ERASED_EXC = "open shortcuts://run-shortcut?name=SW-DLT&input=text&text=EXCEPTION.vars.erasedAll"
    DERROR_EXC = "open shortcuts://run-shortcut?name=SW-DLT&input=text&text=EXCEPTION.vars.downloadError"

    def __init__(self, media_url):
        self.media_url = media_url
        self.out_name = datetime.datetime.today().strftime("%d-%m-%y-%H-%M-%S")

    def validate_setup(self):
        reboot = False
        if "Package(s) not found" in subprocess.getoutput("pip show youtube-dl"):
            self.show_progress("", "12.5", 0, 0)
            subprocess.run("pip -q install --upgrade youtube-dl")
            reboot = True

        self.show_progress("", "25", 0, 0)
        if "Package(s) not found" in subprocess.getoutput("pip show gallery-dl"):
            self.show_progress("", "37.5", 0, 0)
            subprocess.run("pip -q install --upgrade gallery-dl")
            reboot = True

        self.show_progress("", "50", 0, 0)
        if reboot is True:
            raise Exception(self.REBOOT_EXC)

        subprocess.run("cd")
        if os.path.exists("./bin") is False:
            subprocess.run("mkdir bin")
            subprocess.run("cd bin")
            self.show_progress("", "62.5", 0, 0)
            req1 = requests.get(self.FFMPEG_URL)
            with open('./ffmpeg.wasm', 'wb') as ffmpeg:
                ffmpeg.write(req1.content)

            self.show_progress("", "75", 0, 0)
            self.show_progress("", "87.5", 0, 0)
            req2 = requests.get(self.FFPROBE_URL)
            with open('./ffprobe.wasm', 'wb') as ffprobe:
                ffprobe.write(req2.content)

            self.show_progress("", "100", 0, 0)

        else:
            subprocess.run("cd bin")
            if os.path.exists("./ffprobe.wasm") is False:
                self.show_progress("", "62.5", 0, 0)
                req2 = requests.get(self.FFPROBE_URL)
                with open('./ffprobe.wasm', 'wb') as ffprobe:
                    ffprobe.write(req2.content)

            self.show_progress("", "75", 0, 0)
            if os.path.exists("./ffmpeg.wasm") is False:
                self.show_progress("", "87.5", 0, 0)
                req1 = requests.get(self.FFMPEG_URL)
                with open('./ffmpeg.wasm', 'wb') as ffmpeg:
                    ffmpeg.write(req1.content)

            self.show_progress("", "100", 0, 0)
        subprocess.run("jump shortcuts")

    def erase_dependencies(self):
        cleanup_cmds = ("pip uninstall -q -y youtube-dl", "pip uninstall -q -y gallery-dl", "cd", "cd bin",
                        "rm -f ffmpeg.wasm", "rm -f ffprobe.wasm")
        for i in range(len(cleanup_cmds)):
            subprocess.run(cleanup_cmds[i])
            self.show_progress("", "", i + 1, len(cleanup_cmds))

        raise Exception(self.ERASED_EXC)

    def video_download(self):
        video_res = sys.argv[3]
        if video_res == "-d":
            format_opts = {
                "format": "best[ext=mp4]/best/bestvideo[ext=mp4]+bestaudio[ext*=4]/bestvideo[ext!*=4]+bestaudio[ext!*=4]",
                "playlist_items": "1-1",
                "quiet": True,
                "progress_hooks": [self.show_progress],
                "outtmpl": "{}.%(ext)s".format(self.out_name)
            }

        else:
            video_fps = sys.argv[4]
            format_opts = {
                "format": "bestvideo[ext=mp4][height>={0}][fps>={1}]+bestaudio[ext*=4]/bestvideo[ext=mp4][height>={0}][fps<={1}]+bestaudio[ext*=4]/bestvideo[ext!*=4][height>={0}][fps>={1}]+bestaudio[ext!*=4]/bestvideo[ext!*=4][height>={0}][fps<={1}]+bestaudio[ext!*=4]/bestvideo[ext=mp4][height<={0}][fps>={1}]+bestaudio[ext*=4]/bestvideo[ext=mp4][height<={0}][fps<={1}]+bestaudio[ext*=4]/bestvideo[ext!*=4][height<={0}][fps>={1}]+bestaudio[ext!*=4]/bestvideo[ext!*=4][height<={0}][fps<={1}]+bestaudio[ext!*=4]/best[ext=mp4][height>={0}][fps>={1}]/best[ext=mp4][height>={0}][fps<={1}]/best[ext!*=4][height>={0}][fps>={1}]/best[ext!*=4][height>={0}][fps<={1}]/best[ext=mp4][height<={0}][fps>={1}]/best[ext=mp4][height<={0}][fps<={1}]/best[ext!*=4][height<={0}][fps>={1}]/best[ext!*=4][height<={0}][fps<={1}]".format(
                    video_res, video_fps),
                "playlist_items": "1-1",
                "quiet": True,
                "progress_hooks": [self.show_progress],
                "outtmpl": "{}.%(ext)s".format(self.out_name)
            }

        try:
            self.single_ytdl(format_opts)

        except:
            raise Exception(self.DERROR_EXC)

    def audio_download(self):
        format_opts = {
            "format": "bestaudio[ext*=4]/bestaudio[ext=mp3]/best[ext=mp4]/best",
            "playlist_items": "1-1",
            "quiet": True,
            "progress_hooks": [self.show_progress],
            "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "m4a"}],
            "outtmpl": "{}.%(ext)s".format(self.out_name)
        }
        try:
            self.single_ytdl(format_opts)

        except:
            raise Exception(self.DERROR_EXC)

    def single_ytdl(self, format_opts):
        with youtube_dl.YoutubeDL(format_opts) as vid_obj:
            meta_data = vid_obj.extract_info(self.media_url, download=False)
            vid_title = meta_data.get("title", None)
            vid_obj.download([self.media_url])

        re_pattern = re.compile(self.out_name + "\.[\w]{2,4}")
        file_name = re_pattern.search(subprocess.getoutput("ls").replace("\n", " ")).group(0)
        subprocess.run("open shortcuts://run-shortcut?name=SW-DLT&input=text&text=OUTPUT.{0}.TITLE.{1}".format(file_name, urllib.parse.quote(vid_title)))

    def gallery_download(self, gallery_auth_str):
        gallery_range = sys.argv[3]
        gallery_urls = []
        name_count = 0
        iter_count = 0
        file_ext = ""

        if gallery_range == "-all":
            gallery_urls = subprocess.getoutput(
                "gallery-dl -G {0} {1}".format(self.media_url, gallery_auth_str)).splitlines()

        else:
            gallery_urls = subprocess.getoutput(
                "gallery-dl -G {0} --range '{1}' {2}".format(self.media_url, gallery_range, gallery_auth_str)).splitlines()

        subprocess.run("mkdir {}".format(self.out_name))
        subprocess.run("cd {}".format(self.out_name))

        for url in gallery_urls:
            if url.startswith("http"):
                media_get = requests.get(str(url))
                file_ext = mimetypes.guess_extension(media_get.headers['content-type'])
                name_count += 1
                iter_count += 1
                with open('./MEDIA_{0}{1}'.format(name_count, file_ext), 'wb') as item:
                    item.write(media_get.content)

                self.show_progress("", "", iter_count, len(gallery_urls))

            else:
                iter_count += 1

        if name_count < 1:
            subprocess.run("jump shortcuts")
            subprocess.run("rm -r -f {}".format(self.out_name))
            raise Exception(self.DERROR_EXC)

        elif name_count < 2:
            subprocess.run(
                "mv {0} $SHORTCUTS/{1}".format("MEDIA_" + str(name_count) + file_ext, self.out_name + file_ext))
            subprocess.run("rm -r -f {}".format(self.out_name))
            subprocess.run(
                "open shortcuts://run-shortcut?name=SW-DLT&input=text&text=OUTPUT.{0}.TITLE.{0}".format(
                    self.out_name + file_ext))

        else:
            subprocess.run("jump shortcuts")
            shutil.make_archive(self.out_name, "zip", self.out_name)
            subprocess.run("rm -r -f {}".format(self.out_name))
            subprocess.run(
                "open shortcuts://run-shortcut?name=SW-DLT&input=text&text=OUTPUT.{0}.TITLE.{0}".format(
                    self.out_name + ".zip"))

    def playlist_download(self):
        playlist_type = sys.argv[3]
        format_opts = {}

        if playlist_type == "-v":
            format_opts = {
                "format": "best[ext=mp4]/best",
                "quiet": True,
                "progress_hooks": [self.show_progress],
                "outtmpl": "{}/%(title)s.%(ext)s".format(self.out_name)
            }

        else:
            format_opts = {
                "format": "bestaudio[ext*=4]/bestaudio[ext=mp3]/best[ext=mp4]/best",
                "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "m4a"}],
                "quiet": True,
                "progress_hooks": [self.show_progress],
                "outtmpl": "{}/%(title)s.%(ext)s".format(self.out_name)
            }

        try:
            with youtube_dl.YoutubeDL(format_opts) as pl_obj:
                meta_data = pl_obj.extract_info(self.media_url, download=False)
                pl_title = meta_data.get("title", None)
                pl_obj.download([self.media_url])

            shutil.make_archive(self.out_name, "zip", self.out_name)
            subprocess.run("rm -r -f {}".format(self.out_name))
            subprocess.run(
                "open shortcuts://run-shortcut?name=SW-DLT&input=text&text=OUTPUT.{0}.TITLE.{1}".format(
                    self.out_name + ".zip", urllib.parse.quote(pl_title)))

        except:
            raise Exception(self.DERROR_EXC)

    def show_progress(self, ytdl_hook, num="", curr=0, total=0):
        if num != "":
            print("\rProgress: %.1f%s" % (float(num), "%"), end="")
            return
        elif curr != 0:
            print("\rProgress: %.1f%s" % ((100 / total) * curr, "%"), end="")
            return
        else:
            if ytdl_hook["status"] == "downloading":
                print("\rProgress: {}".format(ytdl_hook["_percent_str"].strip()), end="")
                return
            elif ytdl_hook["status"] == "finished":
                print()
                return


def main():
    string_msgs = {
        "video_prompt": "SW-DLT\nDownloading video, custom qualities can take longer to process...",
        "audio_prompt": "SW-DLT\nDownloading audio...",
        "playlist_prompt": "SW-DLT\nDownloading playlist, process will take longer for bigger playlists...",
        "gallery_prompt": "SW-DLT\nDownloading URLs, process will take longer for bigger albums...",
        "gallery_auth_prompt": "SW-DLT\nLog-in required, log-in details are NOT SAVED",
        "erase_prompt": "SW-DLT\nDeleting all dependencies, please wait...",
        "dependency_check": "SW-DLT\nChecking Dependencies..."
    }

    # Arg 1: media url to download, placeholder for erase utility
    # Arg 2: type of download or process to run
    # Arg 3: resolution for video, type for playlist, range for gallery
    # Arg 4: fps for video, auth for gallery download

    sw_dlt_inst = SWDLT(sys.argv[1])
    download_type = sys.argv[2]
    subprocess.run("clear")

    # Pre-download cleanup and check for utility installation
    print(string_msgs["dependency_check"])

    try:
        sw_dlt_inst.validate_setup()

        subprocess.run("rm -f *-*-*-*-*-*.*")
        subprocess.run("rm -r -f *-*-*-*-*-*")
        subprocess.run("clear")

        # Download functions
        if download_type == "-v":
            print(string_msgs["video_prompt"])
            sw_dlt_inst.video_download()

        elif download_type == "-a":
            print(string_msgs["audio_prompt"])
            sw_dlt_inst.audio_download()

        elif download_type == "-p":
            print(string_msgs["playlist_prompt"])
            sw_dlt_inst.playlist_download()

        elif download_type == "-g":
            gallery_auth_str = ""
            if sys.argv[4] == "-auth":
                print(string_msgs["gallery_auth_prompt"])
                user = ""
                passwd = ""
                while user == "":
                    user = input("Enter Username/E-Mail:\n>>")
                    if user == "":
                        print("Username/E-Mail cannot be blank!\n")

                while passwd == "":
                    passwd = input("Enter Password:\n>>")
                    if passwd == "":
                        print("Password cannot be blank!\n")

                gallery_auth_str = "-u {0} -p {1}".format(user, passwd)
                subprocess.run("clear")
                print(string_msgs["gallery_prompt"])

            else:
                print(string_msgs["gallery_prompt"])

            sw_dlt_inst.gallery_download(gallery_auth_str)

        elif download_type == "-e":
            print(string_msgs["erase_prompt"])
            sw_dlt_inst.erase_dependencies()

    except Exception as rt_ex:
        # All exceptions are handled here and sent back to the Shortcut
        subprocess.run(str(rt_ex.args[0]))
        subprocess.run("clear")
        sys.exit()

    # Post download cleaning
    subprocess.run("clear")


if __name__ == "__main__":
    main()
