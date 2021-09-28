# SW-DLT internal script, check Github for documentation.
# Official release through RoutineHub, avoid unknown sources!

import urllib.parse
import subprocess
import mimetypes
import datetime
import hashlib
import shutil
import sys
import re
import os

# Modules not shipped with Python, expected to fail on first run
try:
    import requests
    import youtube_dl

except ModuleNotFoundError:
    pass


# Constants class
class Consts:
    FFMPEG_URL = "https://github.com/holzschu/a-Shell-commands/releases/download/0.1/ffmpeg.wasm"
    FFPROBE_URL = "https://github.com/holzschu/a-Shell-commands/releases/download/0.1/ffprobe.wasm"
    REBOOT_EXC = "shortcuts://run-shortcut?name=SW-DLT&input=text&text=EXCEPTION.vars.restartRequired"
    ERASED_EXC = "shortcuts://run-shortcut?name=SW-DLT&input=text&text=EXCEPTION.vars.erasedAll"
    DERROR_EXC = "shortcuts://run-shortcut?name=SW-DLT&input=text&text=EXCEPTION.vars.downloadError"


class SW_DLT:

    def __init__(self, media_url, file_id):
        self.media_url = media_url
        self.file_id = file_id
        self.date_id = datetime.datetime.today().strftime("%d-%m-%y-%H-%M-%S")

    @staticmethod
    def validate_install():
        reboot = False
        show_progress("", 0, 5)
        if "shortcuts" not in subprocess.getoutput("showmarks"):
            subprocess.getoutput("bookmark shortcuts")

        show_progress("", 1, 5)
        if "Package(s) not found" in subprocess.getoutput("pip show youtube-dl"):
            subprocess.run("pip -q install --disable-pip-version-check --upgrade youtube-dl")
            reboot = True

        show_progress("", 2, 5)
        if "Package(s) not found" in subprocess.getoutput("pip show gallery-dl"):
            subprocess.run("pip -q install --disable-pip-version-check --upgrade gallery-dl")
            reboot = True
        
        show_progress("", 3, 5)
        if reboot:
            raise Exception(Consts.REBOOT_EXC)
        
        subprocess.run("cd")
        # If native FFmpeg is present, removes any wasm version on device. 
        if os.path.exists("{}/bin/ffmpeg".format(os.environ["APPDIR"])):
            subprocess.run("rm -f ./bin/ffmpeg.wasm")
            subprocess.run("rm -f ./bin/ffprobe.wasm")

        # If native FFmpeg is not present, installs any required wasm file
        else:
            if not os.path.exists("./bin"):
                subprocess.run("mkdir bin")

            subprocess.run("cd bin")
            if not os.path.exists("./ffprobe.wasm"):
                req1 = requests.get(Consts.FFPROBE_URL)
                with open('./ffprobe.wasm', 'wb') as ffprobe:
                    ffprobe.write(req1.content)

            show_progress("", 4, 5)
            if not os.path.exists("./ffmpeg.wasm"):
                req2 = requests.get(Consts.FFMPEG_URL)
                with open('./ffmpeg.wasm', 'wb') as ffmpeg:
                    ffmpeg.write(req2.content)

        show_progress("", 5, 5)
        subprocess.run("jump shortcuts")
    
    @staticmethod
    def erase_dependencies():
        cleanup_cmds = ("pip uninstall -q -y youtube-dl", "pip uninstall -q -y gallery-dl", "cd", "rm -f ./bin/ffmpeg.wasm", 
            "rm -f ./bin/ffprobe.wasm")
        for i in range(len(cleanup_cmds)):
            subprocess.run(cleanup_cmds[i])
            show_progress("", i + 1, len(cleanup_cmds))

        raise Exception(Consts.ERASED_EXC)   

    def single_video(self, video_res):
        dl_options = {}
        if video_res == "-d":
            dl_options = {
                "format": "best[ext=mp4]/best/bestvideo[ext=mp4]+bestaudio[ext*=4]/bestvideo[ext!*=4]+bestaudio[ext!*=4]",
                "playlist_items": "1-1",
                "quiet": True,
                "no_warnings": True,
                "progress_hooks": [show_progress],
                "outtmpl": "{}.%(ext)s".format(self.file_id)
            }
        
        else:
            video_fps = sys.argv[4]
            dl_options = {
                "format": "worstvideo[ext=mp4][height>={0}][fps>={1}]+bestaudio[ext*=4]/worstvideo[ext=mp4][height>={0}][fps<={1}]+bestaudio[ext*=4]/worstvideo[ext!*=4][height>={0}][fps>={1}]+bestaudio[ext!*=4]/worstvideo[ext!*=4][height>={0}][fps<={1}]+bestaudio[ext!*=4]/bestvideo[ext=mp4][height<={0}][fps>={1}]+bestaudio[ext*=4]/bestvideo[ext=mp4][height<={0}][fps<={1}]+bestaudio[ext*=4]/bestvideo[ext!*=4][height<={0}][fps>={1}]+bestaudio[ext!*=4]/bestvideo[ext!*=4][height<={0}][fps<={1}]+bestaudio[ext!*=4]/worst[ext=mp4][height>={0}][fps>={1}]/worst[ext=mp4][height>={0}][fps<={1}]/worst[ext!*=4][height>={0}][fps>={1}]/worst[ext!*=4][height>={0}][fps<={1}]/best[ext=mp4][height<={0}][fps>={1}]/best[ext=mp4][height<={0}][fps<={1}]/best[ext!*=4][height<={0}][fps>={1}]/best[ext!*=4][height<={0}][fps<={1}]".format(
                    video_res, video_fps),
                "playlist_items": "1-1",
                "quiet": True,
                "no_warnings": True,
                "progress_hooks": [show_progress],
                "outtmpl": "{}.%(ext)s".format(self.file_id)
            }
        
        try:
            # Returns shortcuts URL redirect with downloaded file data, any exception is re-thrown
            return self.single_download(dl_options)
        
        except:
            raise Exception(Consts.DERROR_EXC)

    def single_audio(self):
        dl_options = {
            "format": "bestaudio[ext*=4]/bestaudio[ext=mp3]/best[ext=mp4]/best",
            "playlist_items": "1-1",
            "quiet": True,
            "no_warnings": True,
            "progress_hooks": [show_progress],
            "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "m4a"}],
            "outtmpl": "{}.%(ext)s".format(self.file_id)
        }
        try:
            # Returns shortcuts URL redirect with downloaded file data, any exception is re-thrown
            return self.single_download(dl_options)

        except:
            raise Exception(Consts.DERROR_EXC)

    def single_download(self, dl_options):
        # Uses YouTube-dl to download single video or audio items
        with youtube_dl.YoutubeDL(dl_options) as vid_obj:
            meta_data = vid_obj.extract_info(self.media_url, download=False)
            vid_title = meta_data.get("title", self.date_id) #2nd argument is alternate title
            vid_obj.download([self.media_url])

        re_pattern = re.compile(self.file_id + "\\.[\\w]{2,4}")
        file_name = re_pattern.search(subprocess.getoutput("ls")).group(0)
        return "shortcuts://run-shortcut?name=SW-DLT&input=text&text=OUTPUT.{0}.TITLE.{1}".format(file_name, urllib.parse.quote(vid_title))

    def gallery_download(self, gallery_range, auth_str):
        gallery_urls = []
        iteration = 1
        item_num = 1
        file_ext = ""

        # Obtaining URL list to download
        if gallery_range == "-all":
            gallery_urls = subprocess.getoutput(
                "gallery-dl -G {0} {1}".format(self.media_url, auth_str)
            ).splitlines()

        else:
            gallery_urls = subprocess.getoutput(
                "gallery-dl -G {0} --range '{1}' {2}".format(self.media_url, gallery_range, auth_str)
            ).splitlines()

        # Creating temp folder to store media
        subprocess.run("mkdir -p {}".format(self.file_id))
        subprocess.run("cd {}".format(self.file_id))

        present_items = subprocess.getoutput("ls")

        for url in gallery_urls:
            if "MEDIA_{}".format(item_num) in present_items:
                item_num += 1
                iteration += 1
                continue
            
            if url.startswith("http"):
                item_get = requests.get(str(url))
                file_ext = mimetypes.guess_extension(item_get.headers['content-type'])
                with open('./MEDIA_{0}{1}'.format(item_num, file_ext), 'wb') as media_item:
                    media_item.write(item_get.content)

                show_progress("", iteration, len(gallery_urls))
                item_num += 1
                iteration += 1
            
            else:
                iteration += 1
        
        # Less than 2 items means no URLs returned, removes temp folder and raises Exception
        if item_num < 2:
            subprocess.run("jump shortcuts")
            subprocess.run("rm -r -f {}".format(self.file_id))
            raise Exception(Consts.DERROR_EXC)

        # Less than 3 items means a single item, removes folder and directly outputs the item
        elif item_num < 3:
            # Moves single item to root of $SHORTCUTS
            subprocess.run(
                "mv {0} $SHORTCUTS/{1}".format("MEDIA_1" + file_ext, self.file_id + file_ext))
    
            subprocess.run("rm -r -f {}".format(self.file_id))
            return "shortcuts://run-shortcut?name=SW-DLT&input=text&text=OUTPUT.{0}.TITLE.{1}".format(
                self.file_id + file_ext, self.date_id + file_ext)

        # For multiple items, zips them and returns zip file
        else:
            subprocess.run("jump shortcuts")
            shutil.make_archive(self.file_id, "zip", self.file_id)
            subprocess.run("rm -r -f {}".format(self.file_id))
            return "shortcuts://run-shortcut?name=SW-DLT&input=text&text=OUTPUT.{0}.TITLE.{1}".format(
                self.file_id + ".zip", self.date_id + ".zip")
        
    def playlist_download(self, playlist_type):
        dl_options = {}

        if playlist_type == "-v":
            dl_options = {
                "format": "best[ext=mp4]/best",
                "quiet": True,
                "no_warnings": True,
                "progress_hooks": [show_progress],
                "outtmpl": "{}/%(title)s.%(ext)s".format(self.file_id)
            }

        else:
            dl_options = {
                "format": "bestaudio[ext*=4]/bestaudio[ext=mp3]/best[ext=mp4]/best",
                "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "m4a"}],
                "quiet": True,
                "no_warnings": True,
                "progress_hooks": [show_progress],
                "outtmpl": "{}/%(title)s.%(ext)s".format(self.file_id)
            }

        try:
            with youtube_dl.YoutubeDL(dl_options) as pl_obj:
                meta_data = pl_obj.extract_info(self.media_url, download=False)
                pl_title = meta_data.get("title", self.date_id) #2nd argument is alternate title
                pl_obj.download([self.media_url])

            shutil.make_archive(self.file_id, "zip", self.file_id)
            subprocess.run("rm -r -f {}".format(self.file_id))
            return "shortcuts://run-shortcut?name=SW-DLT&input=text&text=OUTPUT.{0}.TITLE.{1}".format(
                    self.file_id + ".zip", urllib.parse.quote(pl_title))

        except:
            raise Exception(Consts.DERROR_EXC)


def show_progress(dl_stream, curr=0, total=0):
    # dl_stream is the progress hook from youtube_dl that feeds download status data
    # Other progress types are based on ratio of current item to the total
    if dl_stream == "":
        print("\rProgress: %.1f%s" % ((100 / total) * curr, "%"), end="")
        return
    else:
        if dl_stream["status"] == "downloading":
            print("\rProgress: {}".format(dl_stream["_percent_str"].strip()), end="")
        elif dl_stream["status"] == "finished":
            print()
        return


def auth_prompt():
    # General authentication prompt for password restricted content
    username = ""
    password = ""

    while not username:
        username = input("Enter Username/E-mail:\n>>")
        if not username:
            print("Username/E-mail cannot be blank!\n")
    
    while not password:
        password = input("Enter Password:\n>>")
        if not password:
            print("Password cannot be blank!\n")
    
    return [username, password]


def main():
    # Arg 1: media URL to download, placeholder when using erase utility
    # Arg 2: main process to run
    # Arg 3: resolution for video, type for playlist, range for gallery
    # Arg 4: FPS for video, authentication for gallery download

    info_msgs = {
        "video_prompt": "Video Download\nCustom qualities require processing.",
        "audio_prompt": "Audio Download\nSometimes audio processing is needed.",
        "playlist_prompt": "Playlist Download\nProcess time depends on playlist length.",
        "gallery_prompt": "Gallery Download\nProcess time depends on collection length.",
        "gallery_auth_prompt": "Log-in required, log-in details are NOT SAVED",
        "erase_prompt": "Deleting All Dependencies.",
        "dependency_check": "SW-DLT\nValidating Dependencies."
    }

    # Hashes all arguments to generate unique ID
    file_id = "SW_DLT_DL_{}".format(hashlib.md5(str(sys.argv).encode("utf-8")).hexdigest()[0:20])

    sw_dlt_inst = SW_DLT(sys.argv[1], file_id)
    process_type = sys.argv[2]
    header = ""

    try:
        # Pre-download check and cleanup
        subprocess.run("clear")
        print(info_msgs["dependency_check"])

        sw_dlt_inst.validate_install()
        # If the same partial file is not found deletes all leftovers (important)
        if file_id not in subprocess.getoutput("ls"):
            subprocess.run("rm -f SW_DLT_DL_*.*")
            subprocess.run("rm -r -f SW-DLT_DL_*")
            header = "SW-DLT" 
        else:
            header = "SW-DLT (Resuming Download)"

        subprocess.run("clear")
        print(header)
        # Process selection
        if process_type == "-v":
            print(info_msgs["video_prompt"])
            subprocess.run("open " + sw_dlt_inst.single_video(sys.argv[3]))

        elif process_type == "-a":
            print(info_msgs["audio_prompt"])
            subprocess.run("open " + sw_dlt_inst.single_audio())
        
        elif process_type == "-p":
            print(info_msgs["playlist_prompt"])
            subprocess.run("open " + sw_dlt_inst.playlist_download(sys.argv[3]))
        
        elif process_type == "-g":
            auth_data = []
            auth_str = ""
            if sys.argv[4] == "-auth":
                print(info_msgs["gallery_auth_prompt"])
                auth_data = auth_prompt()
                auth_str = "-u {0} -p {1}".format(auth_data[0], auth_data[1])
                subprocess.run("clear")
                print("{0}\n{1}".format(header, info_msgs["gallery_prompt"]))

            else:
                print(info_msgs["gallery_prompt"])
            
            subprocess.run("open " + sw_dlt_inst.gallery_download(sys.argv[3], auth_str))

        elif process_type == "-e":
            print(info_msgs["erase_prompt"])
            subprocess.run("open " + sw_dlt_inst.erase_dependencies())
        
    except Exception as exc_url:
        # All raised exceptions are handled here and send the user back to the shortcut with a message
        subprocess.run("open " + str(exc_url.args[0]))

    # Post download cleanup
    subprocess.run("clear")


if __name__ == "__main__":
    main()
