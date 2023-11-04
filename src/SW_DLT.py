# SW-DLT script, check Github for documentation.
# Official release through RoutineHub, avoid unknown sources!

import urllib.parse
import contextlib
import subprocess
import mimetypes
import importlib
import datetime
import hashlib
import shutil
import json
import sys
import os

# Modules not shipped with Python, expected to fail on first run
try:
    import requests
    import yt_dlp

except ImportError:
    pass


# Constants class
class Consts:
    CYELLOW, CGREEN, CBLUE, SBOLD, ENDL = "\033[93m", "\033[92m", "\033[94m", "\033[1m", "\033[0m"
    FFMPEG_URL = "https://github.com/holzschu/a-Shell-commands/releases/download/0.1/ffmpeg.wasm"
    FFPROBE_URL = "https://github.com/holzschu/a-Shell-commands/releases/download/0.1/ffprobe.wasm"
    ERASED_EXC = '{"output_code":"exception","exc_path":"vars.erasedAll"}'
    DERROR_EXC = '{"output_code":"exception","exc_path":"vars.downloadError"}'
    UNK_EXC = '{"output_code":"exception","exc_path":"vars.unknownError"}'


class SW_DLT:

    def __init__(self, file_id, *args):
        # args[0]: media URL to download, or placeholder when using erase function
        # args[1]: main process to run
        # args[2] (dependent): resolution for video, type for playlist, or range for gallery
        # args[3] (dependent): framerate for video
        self.media_url = args[0]
        self.file_id = file_id
        self.date_id = datetime.datetime.today().strftime("%d-%m-%y-%H-%M-%S")
        self.ytdlp_globals = {
            "color": "never",
            "quiet": True,
            "no_warnings": True,
            "noprogress": True,
            "progress_hooks": [show_progress],
            "postprocessor_hooks": [format_processing],
        }

        processes = {
            "-v": self.single_video,
            "-a": self.single_audio,
            "-p": self.playlist_download,
            "-g": self.gallery_download,
            "-e": self.erase_dependencies
        }
        self.run = processes[args[1]]
        self.video_res = ""
        self.video_fps = ""
        self.playlist_type = ""
        self.gallery_range = ""

        if len(args) > 2:
            self.video_res = args[2] if args[1] == "-v" else ""
            self.playlist_type = args[2] if args[1] == "-p" else ""
            self.gallery_range = args[2] if args[1] == "-g" else ""

        if len(args) > 3:
            self.video_fps = args[3]

    @staticmethod
    def validate_install():
        revalidate = False

        show_progress("util", 0, 5)
        if importlib.util.find_spec("chardet") is None:
            subprocess.run("pip -q install chardet --disable-pip-version-check --upgrade")
            revalidate = True

        show_progress("util", 1, 5)
        if importlib.util.find_spec("yt_dlp") is None:
            subprocess.run(
                "pip -q install yt-dlp --disable-pip-version-check --upgrade --no-dependencies")
            revalidate = True

        show_progress("util", 2, 5)
        if importlib.util.find_spec("gallery_dl") is None:
            subprocess.run(
                "pip -q install gallery-dl --disable-pip-version-check --upgrade")
            revalidate = True

        show_progress("util", 3, 5)
        if revalidate:
            importlib.invalidate_caches()

        # If native FFmpeg is present, removes any web assembly version on device.
        if os.path.exists(f"{os.environ['APPDIR']}/bin/ffmpeg"):
            with contextlib.suppress(FileNotFoundError):
                os.remove(f"{os.environ['HOME']}/Documents/bin/ffmpeg.wasm")
                os.remove(f"{os.environ['HOME']}/Documents/bin/ffprobe.wasm")

        # Otherwise, installs any required web assembly files
        else:
            os.makedirs(f"{os.environ['HOME']}/Documents/bin", exist_ok=True)
            if not os.path.exists(f"{os.environ['HOME']}/Documents/bin/ffprobe.wasm"):
                req1 = requests.get(Consts.FFPROBE_URL)
                with open(f"{os.environ['HOME']}/Documents/bin/ffprobe.wasm", 'wb') as ffprobe:
                    ffprobe.write(req1.content)

            show_progress("util", 4, 5)
            if not os.path.exists(f"{os.environ['HOME']}/Documents/bin/ffmpeg.wasm"):
                req2 = requests.get(Consts.FFMPEG_URL)
                with open(f"{os.environ['HOME']}/Documents/bin/ffmpeg.wasm", 'wb') as ffmpeg:
                    ffmpeg.write(req2.content)

        show_progress("util", 5, 5)

    @staticmethod
    def erase_dependencies():
        cleanup_cmds = ("pip uninstall -q -y yt-dlp", "pip uninstall -q -y gallery-dl", f"rm -rf {os.environ['HOME']}/Documents/bin/ffmpeg.wasm",
                        f"rm -rf {os.environ['HOME']}/Documents/bin/ffprobe.wasm")
        for i in range(len(cleanup_cmds)):
            subprocess.run(cleanup_cmds[i])
            show_progress("util", i + 1, len(cleanup_cmds))

        raise Exception(Consts.ERASED_EXC)

    def single_video(self):
        priority = [
            f'bestvideo[ext=mp4][height<={self.video_res}][fps<={self.video_fps}]+bestaudio[ext*=4]/',
            f'bestvideo[ext!*=4][height<={self.video_res}][fps<={self.video_fps}]+bestaudio[ext!*=4]/',
            f'best[ext=mp4][height<={self.video_res}][fps<={self.video_fps}]',
            f'best[ext!*=4][height<={self.video_res}][fps<={self.video_fps}]'
        ]
        if self.video_res == "1440" or self.video_res == "2160":
            priority = [priority[1], priority[0], priority[3], priority[2]]

        default_format = "best[ext=mp4]/best/bestvideo[ext=mp4]+bestaudio[ext*=4]/bestvideo[ext!*=4]+bestaudio[ext!*=4]"
        custom_format = ""\
            "bestvideo[ext=mp4][height={0}][fps<={1}]+bestaudio[ext*=4]/"\
            "bestvideo[ext!*=4][height={0}][fps<={1}]+bestaudio[ext!*=4]/"\
            "{2}"\
            "{3}"\
            "best[ext=mp4][height={0}][fps<={1}]/"\
            "best[ext!*=4][height={0}][fps<={1}]/"\
            "{4}"\
            "{5}".format(self.video_res, self.video_fps, *priority)

        dl_options = {
            "format": default_format if self.video_res == "-d" else custom_format,
            "playlist_items": "1-1",
            "outtmpl": f'{self.file_id}.%(ext)s',
            **self.ytdlp_globals
        }

        try:
            # Returns shortcuts redirect URL with downloaded file data, any exception is re-thrown
            return self.single_download(dl_options)

        except:
            raise Exception(Consts.DERROR_EXC)

    def single_audio(self):
        dl_options = {
            "format": "bestaudio[ext*=4]/bestaudio[ext=mp3]/best[ext=mp4]/best",
            "playlist_items": "1-1",
            "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "m4a"}],
            "outtmpl": f'{self.file_id}.%(ext)s',
            **self.ytdlp_globals
        }

        try:
            # Returns shortcuts redirect URL with downloaded file data, any exception is re-thrown
            return self.single_download(dl_options)

        except:
            raise Exception(Consts.DERROR_EXC)

    def single_download(self, dl_options):
        # Uses yt-dlp to download single video or audio items
        with yt_dlp.YoutubeDL(dl_options) as vid_obj:
            meta_data = vid_obj.extract_info(self.media_url, download=False)
            vid_title = meta_data.get("title", self.date_id)
            vid_obj.download([self.media_url])

        for file in os.listdir():
            if file.startswith(self.file_id):
                output = {
                    "output_code": "success",
                    "file_name": file,
                    "file_title": vid_title
                }
                return f'shortcuts://run-shortcut?name=SW-DLT&input=text&text={urllib.parse.quote(json.dumps(output))}'
        raise Exception()

    def gallery_download(self):
        i = 1
        mnum = 1
        try:
            # Obtaining URL list to download
            gallery_urls = subprocess.check_output(
                "gallery-dl -G {0} --range {1}".format(self.media_url, self.gallery_range))
            gallery_urls = gallery_urls.decode("utf-8").splitlines()

            # Creating temp folder to store media
            os.makedirs(self.file_id, exist_ok=True)
            cached = str(os.listdir(self.file_id))

            for url in gallery_urls:
                if f'MEDIA_{mnum}' in cached:
                    mnum += 1
                    i += 1
                    continue

                if url.startswith("http"):
                    req = requests.get(str(url))
                    file_ext = mimetypes.guess_extension(
                        req.headers["content-type"])
                    with open(f'{self.file_id}/MEDIA_{mnum}{file_ext}', "wb") as media_item:
                        media_item.write(req.content)

                    show_progress("manual", i, len(gallery_urls))
                    mnum += 1
                    i += 1

                else:
                    i += 1

            # No URLs returned, removes temp folder and raises Exception
            if mnum < 2:
                shutil.rmtree(self.file_id, True)
                raise Exception()

            # Single item, removes temp folder and directly outputs the item
            elif mnum < 3:
                os.replace("{0}/{1}".format(self.file_id, "MEDIA_1" + file_ext),
                           "{0}/{1}".format(os.environ["SHORTCUTS"], self.file_id + file_ext))

                shutil.rmtree(self.file_id, True)
                output = {
                    "output_code": "success",
                    "file_name": self.file_id + file_ext,
                    "file_title": self.date_id
                }

            # Mutiple items, zips temp folder and returns it, removes temp folder
            else:
                shutil.make_archive(self.file_id, "zip", self.file_id)
                shutil.rmtree(self.file_id, True)
                output = {
                    "output_code": "success",
                    "file_name": self.file_id + ".zip",
                    "file_title": self.date_id
                }

            return f'shortcuts://run-shortcut?name=SW-DLT&input=text&text={urllib.parse.quote(json.dumps(output))}'
        except:
            raise Exception(Consts.DERROR_EXC)

    def playlist_download(self):
        dl_options = {
            "format": "best[ext=mp4]/best" if self.playlist_type == "-v" else "bestaudio[ext*=4]/bestaudio[ext=mp3]/best[ext=mp4]/best",
            "postprocessors": [] if self.playlist_type == "-v" else [{"key": "FFmpegExtractAudio", "preferredcodec": "m4a"}],
            "outtmpl": f'{self.file_id}/%(title)s.%(ext)s',
            **self.ytdlp_globals
        }

        try:
            with yt_dlp.YoutubeDL(dl_options) as pl_obj:
                meta_data = pl_obj.extract_info(self.media_url, download=False)
                pl_title = meta_data.get("title", self.date_id)
                pl_obj.download([self.media_url])

            shutil.make_archive(self.file_id, "zip", self.file_id)
            shutil.rmtree(self.file_id, True)
            output = {
                "output_code": "success",
                "file_name": self.file_id + ".zip",
                "file_title": pl_title
            }
            return f'shortcuts://run-shortcut?name=SW-DLT&input=text&text={urllib.parse.quote(json.dumps(output))}'

        except:
            raise Exception(Consts.DERROR_EXC)


def show_progress(data_stream, curr=0, total=0):
    # data_stream type of data received, can be manual (for gallery-dl downloads), util (for utility processes)
    # it can also be yt-dlp download data streams
    if data_stream == "manual":
        if curr != total:
            print(
                f'\rDownloading: {Consts.CYELLOW}{curr/total:.1%}{Consts.ENDL}', end="")
            return
        print(f'\x1b[1K\r{Consts.CGREEN}Downloaded{Consts.ENDL}')
    elif data_stream == "util":
        print(
            f'\rLoading: {Consts.CYELLOW}{curr/total:.1%}{Consts.ENDL}', end="")
        return
    else:
        if data_stream["status"] == "downloading":
            print(
                f"\rDownloading: {Consts.CYELLOW}{data_stream['_percent_str'].strip()}{Consts.ENDL}", end="")
        elif data_stream["status"] == "finished":
            print(f'\x1b[1K\r{Consts.CGREEN}Downloaded{Consts.ENDL}')
    return


def format_processing(process_stream):
    if process_stream["status"] == "started":
        print(f'\r{Consts.CYELLOW}Processing{Consts.ENDL}', end="")
    elif process_stream["status"] == "finished":
        print(f'\x1b[1K\r{Consts.CGREEN}Processed{Consts.ENDL}')
    return


def main():
    info_msgs = {
        "-v": f'{Consts.CBLUE}Video Download{Consts.ENDL}\n{Consts.CYELLOW}Custom qualities require processing{Consts.ENDL}',
        "-a": f'{Consts.CBLUE}Audio Download{Consts.ENDL}\n{Consts.CYELLOW}Sometimes audio processing is needed{Consts.ENDL}',
        "-p": f'{Consts.CBLUE}Playlist Download{Consts.ENDL}\n{Consts.CYELLOW}Process time depends on playlist length{Consts.ENDL}',
        "-g": f'{Consts.CBLUE}Gallery Download{Consts.ENDL}\n{Consts.CYELLOW}Process time depends on collection length{Consts.ENDL}',
        "-e": f'{Consts.CYELLOW}Deleting All Dependencies{Consts.ENDL}',
        "dep_check": f'{Consts.CBLUE}Preparing{Consts.ENDL}\n{Consts.CYELLOW}Validating Dependencies{Consts.ENDL}'
    }
    try:
        # Hashes all arguments to generate unique ID
        file_id = "SW_DLT_DL_{}".format(hashlib.md5(
            str(sys.argv).encode("utf-8")).hexdigest()[0:20])

        sw_dlt_inst = SW_DLT(file_id, *sys.argv[1:])
        header = f'{Consts.SBOLD}SW-DLT{Consts.ENDL}'

        # Pre-download check and cleanup
        subprocess.run("clear")
        print(header)
        print(info_msgs["dep_check"])

        sw_dlt_inst.validate_install()
        # If the same partial file is not found, deletes all leftovers (important)
        for file in os.listdir():
            if file.startswith("SW-DLT_DL_") and not file.startswith(file_id):
                if os.path.isdir(file):
                    shutil.rmtree(file)
                    continue
                os.remove(file)
            elif file.startswith(file_id):
                header = f'{Consts.SBOLD}SW-DLT (Resuming Download){Consts.ENDL}'

        subprocess.run("clear")
        print(header)
        print(info_msgs[sys.argv[2]])
        return sw_dlt_inst.run()

    except Exception as exc_url:
        # All raised exceptions are handled here and send the user back to the shortcut with a message
        if str(exc_url.args[0]) not in [Consts.DERROR_EXC, Consts.revalidate_EXC, Consts.ERASED_EXC]:
            return f'shortcuts://run-shortcut?name=SW-DLT&input=text&text={urllib.parse.quote(Consts.UNK_EXC)}'
        return f'shortcuts://run-shortcut?name=SW-DLT&input=text&text={urllib.parse.quote(str(exc_url.args[0]))}'


if __name__ == "__main__":
    subprocess.run("open " + main())
    # Post-run cleanup
    subprocess.run("clear")
