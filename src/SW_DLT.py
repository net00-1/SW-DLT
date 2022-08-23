# SW-DLT script, check Github for documentation.
# Official release through RoutineHub, avoid unknown sources!

import urllib.parse
import subprocess
import mimetypes
import datetime
import hashlib
import shutil
import sys
import os

# Modules not shipped with Python, expected to fail on first run
try:
    import requests
    import yt_dlp

except ModuleNotFoundError:
    pass


# Constants class
class Consts:
    FFMPEG_URL = "https://github.com/holzschu/a-Shell-commands/releases/download/0.1/ffmpeg.wasm"
    FFPROBE_URL = "https://github.com/holzschu/a-Shell-commands/releases/download/0.1/ffprobe.wasm"
    REBOOT_EXC = "shortcuts://run-shortcut?name=SW-DLT&input=text&text=EXCEPTION.vars.restartRequired"
    ERASED_EXC = "shortcuts://run-shortcut?name=SW-DLT&input=text&text=EXCEPTION.vars.erasedAll"
    DERROR_EXC = "shortcuts://run-shortcut?name=SW-DLT&input=text&text=EXCEPTION.vars.downloadError"
    CYELLOW, CGREEN, CBLUE, SBOLD, ENDL = "\033[93m", "\033[92m", "\033[94m" , "\033[1m", "\033[0m"


class SW_DLT:

    def __init__(self, media_url, file_id):
        self.media_url = media_url
        self.file_id = file_id
        self.date_id = datetime.datetime.today().strftime("%d-%m-%y-%H-%M-%S")
        self.global_options = {
            "quiet": True,
            "no_warnings": True,
            "noprogress": True,
            "progress_hooks": [show_progress],
            "postprocessor_hooks": [format_processing],
        }

    @staticmethod
    def validate_install():
        reboot = False
        show_progress("util", 0, 5)
        if "shortcuts" not in subprocess.getoutput("showmarks"):
            subprocess.run("bookmark shortcuts")

        show_progress("util", 1, 5)
        if "Package(s) not found" in subprocess.getoutput("pip show yt-dlp"):
            subprocess.run("pip -q install yt-dlp --disable-pip-version-check --upgrade --no-dependencies")
            reboot = True

        show_progress("util", 2, 5)
        if "Package(s) not found" in subprocess.getoutput("pip show gallery-dl"):
            subprocess.run("pip -q install gallery-dl --disable-pip-version-check --upgrade")
            reboot = True

        show_progress("util", 3, 5)
        if reboot:
            raise Exception(Consts.REBOOT_EXC)

        subprocess.run("cd")
        # If native FFmpeg is present, removes any wasm version on device.
        if os.path.exists(f"{os.environ['APPDIR']}/bin/ffmpeg"):
            subprocess.run("rm -f ./bin/ffmpeg.wasm")
            subprocess.run("rm -f ./bin/ffprobe.wasm")

        # If native FFmpeg is not present, installs any required wasm files
        else:
            if not os.path.exists("./bin"):
                subprocess.run("mkdir bin")

            subprocess.run("cd bin")
            if not os.path.exists("./ffprobe.wasm"):
                req1 = requests.get(Consts.FFPROBE_URL)
                with open('./ffprobe.wasm', 'wb') as ffprobe:
                    ffprobe.write(req1.content)

            show_progress("util", 4, 5)
            if not os.path.exists("./ffmpeg.wasm"):
                req2 = requests.get(Consts.FFMPEG_URL)
                with open('./ffmpeg.wasm', 'wb') as ffmpeg:
                    ffmpeg.write(req2.content)

        show_progress("util", 5, 5)
        subprocess.run("jump shortcuts")

    @staticmethod
    def erase_dependencies():
        cleanup_cmds = ("pip uninstall -q -y yt-dlp", "pip uninstall -q -y gallery-dl", "cd", "rm -f ./bin/ffmpeg.wasm",
            "rm -f ./bin/ffprobe.wasm")
        for i in range(len(cleanup_cmds)):
            subprocess.run(cleanup_cmds[i])
            show_progress("util", i + 1, len(cleanup_cmds))

        raise Exception(Consts.ERASED_EXC)

    def single_video(self, video_res, video_fps):
        format_priority = [
            "bestvideo[ext=mp4][height<={0}][fps<={1}]+bestaudio[ext*=4]/"\
            "bestvideo[ext!*=4][height<={0}][fps<={1}]+bestaudio[ext!*=4]/".format(video_res, video_fps),
            "best[ext=mp4][height<={0}][fps<={1}]"\
            "best[ext!*=4][height<={0}][fps<={1}]".format(video_res, video_fps)
        ]
        if video_res == "1440" or video_res == "2160":
            format_priority = [
            "bestvideo[ext!*=4][height<={0}][fps<={1}]+bestaudio[ext!*=4]/"\
            "bestvideo[ext=mp4][height<={0}][fps<={1}]+bestaudio[ext*=4]/".format(video_res, video_fps),
            "best[ext!*=4][height<={0}][fps<={1}]"\
            "best[ext=mp4][height<={0}][fps<={1}]".format(video_res, video_fps)
        ]

        default_format = "best[ext=mp4]/best/bestvideo[ext=mp4]+bestaudio[ext*=4]/bestvideo[ext!*=4]+bestaudio[ext!*=4]"
        custom_format = ""\
            "bestvideo[ext=mp4][height={0}][fps<={1}]+bestaudio[ext*=4]/"\
            "bestvideo[ext!*=4][height={0}][fps<={1}]+bestaudio[ext!*=4]/"\
            "{2}"\
            "best[ext=mp4][height={0}][fps<={1}]/"\
            "best[ext!*=4][height={0}][fps<={1}]/"\
            "{3}".format(video_res, video_fps, format_priority[0], format_priority[1])

        dl_options = {
            "format": default_format if video_res == "-d" else custom_format,
            "playlist_items": "1-1",
            "outtmpl": f"{self.file_id}.%(ext)s",
            **self.global_options
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
            "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "m4a"}],
            "outtmpl": f"{self.file_id}.%(ext)s",
            **self.global_options
        }

        try:
            # Returns shortcuts URL redirect with downloaded file data, any exception is re-thrown
            return self.single_download(dl_options)

        except:
            raise Exception(Consts.DERROR_EXC)

    def single_download(self, dl_options):
        # Uses yt-dlp to download single video or audio items
        with yt_dlp.YoutubeDL(dl_options) as vid_obj:
            meta_data = vid_obj.extract_info(self.media_url, download=False)
            vid_title = meta_data.get("title", self.date_id) # 2nd argument is alternate title
            vid_obj.download([self.media_url])

        for file in subprocess.getoutput("ls").splitlines():
            if file.startswith(self.file_id):
                return f"shortcuts://run-shortcut?name=SW-DLT&input=text&text=OUTPUT.{file}.TITLE.{urllib.parse.quote(vid_title)}"
        raise Exception()

    def gallery_download(self, gallery_range, auth_str):
        gallery_urls = []
        iteration = 1
        item_num = 1

        # Obtaining URL list to download
        gallery_urls = subprocess.getoutput(
                "gallery-dl -G {0}{1}{2}".format(self.media_url, " " if gallery_range == "-all" else f" --range '{gallery_range}' ", auth_str)
            ).splitlines()

        # Creating temp folder to store media
        subprocess.run(f'mkdir -p {self.file_id}')
        subprocess.run(f'cd {self.file_id}')
        present_items = subprocess.getoutput("ls")
        
        for url in gallery_urls:
            if f"MEDIA_{item_num}" in present_items:
                item_num += 1
                iteration += 1
                continue

            if url.startswith("http"):
                item_get = requests.get(str(url))
                file_ext = mimetypes.guess_extension(item_get.headers["content-type"])
                with open(f"./MEDIA_{item_num}{file_ext}", "wb") as media_item:
                    media_item.write(item_get.content)

                show_progress("manual", iteration, len(gallery_urls))
                item_num += 1
                iteration += 1

            else:
                iteration += 1

        # Less than 2 items means no URLs returned, removes temp folder and raises Exception
        if item_num < 2:
            subprocess.run("jump shortcuts")
            subprocess.run(f"rm -r -f {self.file_id}")
            raise Exception(Consts.DERROR_EXC)

        # Less than 3 items means a single item, removes folder and directly outputs the item
        elif item_num < 3:
            # Moves single item to root of $SHORTCUTS
            subprocess.run(
                "mv {0} $SHORTCUTS/{1}".format("MEDIA_1" + file_ext, self.file_id + file_ext))

            subprocess.run(f"rm -r -f {self.file_id}")
            return "shortcuts://run-shortcut?name=SW-DLT&input=text&text=OUTPUT.{0}.TITLE.{1}".format(
                self.file_id + file_ext, self.date_id + file_ext)

        # For multiple items, zips them and returns zip file
        else:
            subprocess.run("jump shortcuts")
            shutil.make_archive(self.file_id, "zip", self.file_id)
            subprocess.run(f"rm -r -f {self.file_id}")
            return "shortcuts://run-shortcut?name=SW-DLT&input=text&text=OUTPUT.{0}.TITLE.{1}".format(
                self.file_id + ".zip", self.date_id + ".zip")

    def playlist_download(self, playlist_type):
        dl_options = {
            "format": "best[ext=mp4]/best" if playlist_type == "-v" else "bestaudio[ext*=4]/bestaudio[ext=mp3]/best[ext=mp4]/best",
            "postprocessors": [] if playlist_type == "-v" else [{"key": "FFmpegExtractAudio", "preferredcodec": "m4a"}],
            "outtmpl": f"{self.file_id}/%(title)s.%(ext)s",
            **self.global_options
        }

        try:
            with yt_dlp.YoutubeDL(dl_options) as pl_obj:
                meta_data = pl_obj.extract_info(self.media_url, download=False)
                pl_title = meta_data.get("title", self.date_id) #2nd argument is alternate title
                pl_obj.download([self.media_url])

            shutil.make_archive(self.file_id, "zip", self.file_id)
            subprocess.run(f"rm -r -f {self.file_id}")
            return "shortcuts://run-shortcut?name=SW-DLT&input=text&text=OUTPUT.{0}.TITLE.{1}".format(
                    self.file_id + ".zip", urllib.parse.quote(pl_title))

        except:
            raise Exception(Consts.DERROR_EXC)


def show_progress(data_stream, curr=0, total=0):
    # data_stream type of data received, can be manual (for gallery-dl downloads), util (for utility processes)
    # it can also be yt-dlp download data streams
    if data_stream == "manual":
        if curr != total:
            print(f"\rDownloading: {Consts.CYELLOW}{curr/total:.1%}{Consts.ENDL}", end="")
            return
        print(f"\x1b[1K\r{Consts.CGREEN}Downloaded{Consts.ENDL}")
    elif data_stream == "util":
        print(f"\rLoading: {Consts.CYELLOW}{curr/total:.1%}{Consts.ENDL}", end="")
        return
    else:
        if data_stream["status"] == "downloading":
            print(f"\rDownloading: {Consts.CYELLOW}{data_stream['_percent_str'].strip()}{Consts.ENDL}", end="")
        elif data_stream["status"] == "finished":
            print(f"\x1b[1K\r{Consts.CGREEN}Downloaded{Consts.ENDL}")
    return


def format_processing(process_stream):
    if process_stream["status"] == "started":
        print(f"\r{Consts.CYELLOW}Processing{Consts.ENDL}", end="")
    elif process_stream["status"] == "finished":
        print(f"\x1b[1K\r{Consts.CGREEN}Processed{Consts.ENDL}")
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


def main(self=None, media_url=None, process_type=None, res_pltype_range=None, fps_auth=None):
    # Arg 0: self instance, not used by the script
    # Arg 1: media URL to download OR placeholder when using erase utility
    # Arg 2: main process to run
    # Arg 3: resolution for video OR type for playlist OR range for gallery
    # Arg 4: FPS for video OR authentication for gallery download

    info_msgs = {
        "video_prompt": f"{Consts.CBLUE}Video Download{Consts.ENDL}\n{Consts.CYELLOW}Custom qualities require processing{Consts.ENDL}",
        "audio_prompt": f"{Consts.CBLUE}Audio Download{Consts.ENDL}\n{Consts.CYELLOW}Sometimes audio processing is needed{Consts.ENDL}",
        "playlist_prompt": f"{Consts.CBLUE}Playlist Download{Consts.ENDL}\n{Consts.CYELLOW}Process time depends on playlist length{Consts.ENDL}",
        "gallery_prompt": f"{Consts.CBLUE}Gallery Download{Consts.ENDL}\n{Consts.CYELLOW}Process time depends on collection length{Consts.ENDL}",
        "gallery_auth_prompt": f"{Consts.CYELLOW}Log-in required, log-in details are NOT SAVED{Consts.ENDL}",
        "erase_prompt": f"{Consts.CYELLOW}Deleting All Dependencies{Consts.ENDL}",
        "dependency_check": f"{Consts.CBLUE}Preparing{Consts.ENDL}\n{Consts.CYELLOW}Validating Dependencies{Consts.ENDL}"
    }

    # Hashes all arguments to generate unique ID
    file_id = "SW_DLT_DL_{}".format(hashlib.md5(str([self, media_url, process_type, res_pltype_range, fps_auth])
    .encode("utf-8"))
    .hexdigest()[0:20])

    sw_dlt_inst = SW_DLT(media_url, file_id)
    header = f"{Consts.SBOLD}SW-DLT{Consts.ENDL}"

    try:
        # Pre-download check and cleanup
        subprocess.run("clear")
        print(header)
        print(info_msgs["dependency_check"])

        sw_dlt_inst.validate_install()
        # If the same partial file is not found, deletes all leftovers (important)
        if file_id not in subprocess.getoutput("ls"):
            subprocess.run("rm -f SW_DLT_DL_*.*")
            subprocess.run("rm -r -f SW-DLT_DL_*")
            pass
        else:
            header = f"{Consts.SBOLD}SW-DLT (Resuming Download){Consts.ENDL}"

        subprocess.run("clear")
        print(header)
        # Process selection
        if process_type == "-v":
            print(info_msgs["video_prompt"])
            return sw_dlt_inst.single_video(res_pltype_range, fps_auth)

        elif process_type == "-a":
            print(info_msgs["audio_prompt"])
            return sw_dlt_inst.single_audio()

        elif process_type == "-p":
            print(info_msgs["playlist_prompt"])
            return sw_dlt_inst.playlist_download(res_pltype_range)

        elif process_type == "-g":
            auth_str = ""
            if fps_auth == "-auth":
                print(info_msgs["gallery_auth_prompt"])
                auth_str = "-u {0} -p {1}".format(*auth_prompt())
                subprocess.run("clear")
                print("{0}\n{1}".format(header, info_msgs["gallery_prompt"]))

            else:
                print(info_msgs["gallery_prompt"])

            return sw_dlt_inst.gallery_download(res_pltype_range, auth_str)

        elif process_type == "-e":
            print(info_msgs["erase_prompt"])
            return sw_dlt_inst.erase_dependencies()

    except Exception as exc_url:
        # All raised exceptions are handled here and send the user back to the shortcut with a message
        return str(exc_url.args[0])


if __name__ == "__main__":
    subprocess.run("open " + main(*sys.argv))
    # Post-run cleanup
    subprocess.run("clear")
