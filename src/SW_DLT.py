# SW-DLT script, do not copy without permission!

import urllib.parse
import subprocess
import mimetypes
import datetime
import hashlib
import shutil
import sys
import re
import os

try:
    import requests
    import youtube_dl

except ModuleNotFoundError:
    pass


class SWDLT:
    FFMPEG_URL = "https://github.com/holzschu/a-Shell-commands/releases/download/0.1/ffmpeg.wasm"
    FFPROBE_URL = "https://github.com/holzschu/a-Shell-commands/releases/download/0.1/ffprobe.wasm"
    REBOOT_EXC = "open shortcuts://run-shortcut?name=SW-DLT&input=text&text=EXCEPTION.vars.restartRequired"
    ERASED_EXC = "open shortcuts://run-shortcut?name=SW-DLT&input=text&text=EXCEPTION.vars.erasedAll"
    DERROR_EXC = "open shortcuts://run-shortcut?name=SW-DLT&input=text&text=EXCEPTION.vars.downloadError"

    def __init__(self, media_url, dl_identifier):
        self.media_url = media_url
        self.dl_identifier = dl_identifier
        self.date_name = datetime.datetime.today().strftime("%d-%m-%y-%H-%M-%S")

    def validate_setup(self):
        reboot = False
        if "Package(s) not found" in subprocess.getoutput("pip show youtube-dl"):
            show_progress("", "12.5", 0, 0)
            subprocess.run("pip -q install --upgrade youtube-dl")
            reboot = True

        show_progress("", "25", 0, 0)
        if "Package(s) not found" in subprocess.getoutput("pip show gallery-dl"):
            show_progress("", "37.5", 0, 0)
            subprocess.run("pip -q install --upgrade gallery-dl")
            reboot = True

        show_progress("", "50", 0, 0)
        if reboot is True:
            raise Exception(self.REBOOT_EXC)

        subprocess.run("cd")
        if os.path.exists("./bin") is False:
            subprocess.run("mkdir bin")

        subprocess.run("cd bin")
        show_progress("", "62.5", 0, 0)

        if os.path.exists("./ffprobe.wasm") is False:
            req1 = requests.get(self.FFPROBE_URL)
            with open('./ffprobe.wasm', 'wb') as ffprobe:
                ffprobe.write(req1.content)

        show_progress("", "75", 0, 0)
        show_progress("", "87.5", 0, 0)
        if os.path.exists("{}/bin/ffmpeg".format(os.environ["APPDIR"])):
            subprocess.run("rm -f ./ffmpeg.wasm")
        else:
            if os.path.exists("./ffmpeg.wasm") is False:
                req2 = requests.get(self.FFMPEG_URL)
                with open('./ffmpeg.wasm', 'wb') as ffmpeg:
                    ffmpeg.write(req2.content)

        show_progress("", "100", 0, 0)
        subprocess.run("jump shortcuts")

    def erase_dependencies(self):
        cleanup_cmds = ("pip uninstall -q -y youtube-dl", "pip uninstall -q -y gallery-dl", "cd", "cd bin",
                        "rm -f ffmpeg.wasm", "rm -f ffprobe.wasm")
        for i in range(len(cleanup_cmds)):
            subprocess.run(cleanup_cmds[i])
            show_progress("", "", i + 1, len(cleanup_cmds))

        raise Exception(self.ERASED_EXC)

    def video_download(self):
        video_res = sys.argv[3]
        if video_res == "-d":
            format_opts = {
                "format": "best[ext=mp4]/best/bestvideo[ext=mp4]+bestaudio[ext*=4]/bestvideo[ext!*=4]+bestaudio[ext!*=4]",
                "playlist_items": "1-1",
                "quiet": True,
                "progress_hooks": [show_progress],
                "outtmpl": "{}.%(ext)s".format(self.dl_identifier)
            }

        else:
            video_fps = sys.argv[4]
            format_opts = {
                "format": "bestvideo[ext=mp4][height>={0}][fps>={1}]+bestaudio[ext*=4]/bestvideo[ext=mp4][height>={0}][fps<={1}]+bestaudio[ext*=4]/bestvideo[ext!*=4][height>={0}][fps>={1}]+bestaudio[ext!*=4]/bestvideo[ext!*=4][height>={0}][fps<={1}]+bestaudio[ext!*=4]/bestvideo[ext=mp4][height<={0}][fps>={1}]+bestaudio[ext*=4]/bestvideo[ext=mp4][height<={0}][fps<={1}]+bestaudio[ext*=4]/bestvideo[ext!*=4][height<={0}][fps>={1}]+bestaudio[ext!*=4]/bestvideo[ext!*=4][height<={0}][fps<={1}]+bestaudio[ext!*=4]/best[ext=mp4][height>={0}][fps>={1}]/best[ext=mp4][height>={0}][fps<={1}]/best[ext!*=4][height>={0}][fps>={1}]/best[ext!*=4][height>={0}][fps<={1}]/best[ext=mp4][height<={0}][fps>={1}]/best[ext=mp4][height<={0}][fps<={1}]/best[ext!*=4][height<={0}][fps>={1}]/best[ext!*=4][height<={0}][fps<={1}]".format(
                    video_res, video_fps),
                "playlist_items": "1-1",
                "quiet": True,
                "progress_hooks": [show_progress],
                "outtmpl": "{}.%(ext)s".format(self.dl_identifier)
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
            "progress_hooks": [show_progress],
            "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "m4a"}],
            "outtmpl": "{}.%(ext)s".format(self.dl_identifier)
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

        re_pattern = re.compile(self.dl_identifier + "\\.[\\w]{2,4}")
        file_name = re_pattern.search(subprocess.getoutput("ls").replace("\n", " ")).group(0)
        subprocess.run("open shortcuts://run-shortcut?name=SW-DLT&input=text&text=OUTPUT.{0}.TITLE.{1}".format(file_name, urllib.parse.quote(vid_title)))

    def gallery_download(self, gallery_auth_str):
        gallery_range = sys.argv[3]
        gallery_urls = []
        name_count = 1
        iter_count = 1
        file_ext = ""

        if gallery_range == "-all":
            gallery_urls = subprocess.getoutput(
                "gallery-dl -G {0} {1}".format(self.media_url, gallery_auth_str)).splitlines()

        else:
            gallery_urls = subprocess.getoutput(
                "gallery-dl -G {0} --range '{1}' {2}".format(self.media_url, gallery_range, gallery_auth_str)).splitlines()

        subprocess.run("mkdir -p {}".format(self.dl_identifier))
        subprocess.run("cd {}".format(self.dl_identifier))
        present_items = subprocess.getoutput("ls")

        for url in gallery_urls:
            if "MEDIA_{}".format(name_count) in present_items:
                name_count += 1
                iter_count += 1
                continue

            if url.startswith("http"):
                media_get = requests.get(str(url))
                file_ext = mimetypes.guess_extension(media_get.headers['content-type'])
                with open('./MEDIA_{0}{1}'.format(name_count, file_ext), 'wb') as item:
                    item.write(media_get.content)

                show_progress("", "", iter_count, len(gallery_urls))
                name_count += 1
                iter_count += 1

            else:
                iter_count += 1

        if name_count < 2:
            subprocess.run("jump shortcuts")
            subprocess.run("rm -r -f {}".format(self.dl_identifier))
            raise Exception(self.DERROR_EXC)

        elif name_count < 3:
            subprocess.run(
                "mv {0} $SHORTCUTS/{1}".format("MEDIA_1" + file_ext, self.dl_identifier + file_ext))
            subprocess.run("rm -r -f {}".format(self.dl_identifier))
            subprocess.run(
                "open shortcuts://run-shortcut?name=SW-DLT&input=text&text=OUTPUT.{0}.TITLE.{1}".format(
                    self.dl_identifier + file_ext, self.date_name + file_ext))

        else:
            subprocess.run("jump shortcuts")
            shutil.make_archive(self.dl_identifier, "zip", self.dl_identifier)
            subprocess.run("rm -r -f {}".format(self.dl_identifier))
            subprocess.run(
                "open shortcuts://run-shortcut?name=SW-DLT&input=text&text=OUTPUT.{0}.TITLE.{1}".format(
                    self.dl_identifier + ".zip", self.date_name + ".zip"))

    def playlist_download(self):
        playlist_type = sys.argv[3]
        format_opts = {}

        if playlist_type == "-v":
            format_opts = {
                "format": "best[ext=mp4]/best",
                "quiet": True,
                "progress_hooks": [show_progress],
                "outtmpl": "{}/%(title)s.%(ext)s".format(self.dl_identifier)
            }

        else:
            format_opts = {
                "format": "bestaudio[ext*=4]/bestaudio[ext=mp3]/best[ext=mp4]/best",
                "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "m4a"}],
                "quiet": True,
                "progress_hooks": [show_progress],
                "outtmpl": "{}/%(title)s.%(ext)s".format(self.dl_identifier)
            }

        try:
            with youtube_dl.YoutubeDL(format_opts) as pl_obj:
                meta_data = pl_obj.extract_info(self.media_url, download=False)
                pl_title = meta_data.get("title", None)
                pl_obj.download([self.media_url])

            shutil.make_archive(self.dl_identifier, "zip", self.dl_identifier)
            subprocess.run("rm -r -f {}".format(self.dl_identifier))
            subprocess.run(
                "open shortcuts://run-shortcut?name=SW-DLT&input=text&text=OUTPUT.{0}.TITLE.{1}".format(
                    self.dl_identifier + ".zip", urllib.parse.quote(pl_title)))

        except:
            raise Exception(self.DERROR_EXC)


def show_progress(ytdl_hook, num="", curr=0, total=0):
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
        "video_prompt": "Video Download\nCustom qualities require processing.",
        "audio_prompt": "Audio Download\nSometimes audio processing is needed.",
        "playlist_prompt": "Playlist Download\nProcess time depends on playlist length.",
        "gallery_prompt": "Gallery Download\nProcess time depends on collection length.",
        "gallery_auth_prompt": "Log-in required, log-in details are NOT SAVED",
        "erase_prompt": "Deleting All Dependencies.",
        "dependency_check": "SW-DLT\nValidating Dependencies."
    }

    # Arg 1: media URL to download, placeholder for erase utility
    # Arg 2: main process to run
    # Arg 3: resolution for video, type for playlist, range for gallery
    # Arg 4: FPS for video, authentication for gallery download

    dl_identifier = "SW_DLT_DL_{}".format(hashlib.md5(str(sys.argv).encode("utf-8")).hexdigest()[0:20])
    sw_dlt_inst = SWDLT(sys.argv[1], dl_identifier)
    process_type = sys.argv[2]
    header = ""

    # Pre-download cleanup and validation of installation
    subprocess.run("clear")
    print(string_msgs["dependency_check"])

    try:
        sw_dlt_inst.validate_setup()
        if dl_identifier not in subprocess.getoutput("ls"):
            subprocess.run("rm -f SW_DLT_DL_*.*")
            subprocess.run("rm -r -f SW-DLT_DL_*")
            subprocess.run("clear")
            header = "SW-DLT"
        else:
            subprocess.run("clear")
            header = "SW-DLT (Resuming Download)"

        print(header)
        # Main Functions
        if process_type == "-v":
            print(string_msgs["video_prompt"])
            sw_dlt_inst.video_download()

        elif process_type == "-a":
            print(string_msgs["audio_prompt"])
            sw_dlt_inst.audio_download()

        elif process_type == "-p":
            print(string_msgs["playlist_prompt"])
            sw_dlt_inst.playlist_download()

        elif process_type == "-g":
            gallery_auth_str = ""
            if sys.argv[4] == "-auth":
                print(string_msgs["gallery_auth_prompt"])
                user = ""
                passwd = ""
                while not user:
                    user = input("Enter Username/E-Mail:\n>>")
                    if not user:
                        print("Username/E-Mail cannot be blank!\n")

                while not passwd:
                    passwd = input("Enter Password:\n>>")
                    if not passwd:
                        print("Password cannot be blank!\n")

                gallery_auth_str = "-u {0} -p {1}".format(user, passwd)
                subprocess.run("clear")
                print("{0}\n{1}".format(header, string_msgs["gallery_prompt"]))

            else:
                print(string_msgs["gallery_prompt"])

            sw_dlt_inst.gallery_download(gallery_auth_str)

        elif process_type == "-e":
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
