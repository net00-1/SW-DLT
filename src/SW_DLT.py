# SW-DLT script, check Github for documentation.
# Official release on GitHub, avoid unknown sources

import urllib.parse
import subprocess
import importlib
import datetime
import hashlib
import shutil
import base64
import json
import sys
import os

# Constants class
class Consts:
    CYELLOW, CGREEN, CBLUE, SBOLD, ENDL = "\033[93m", "\033[92m", "\033[94m", "\033[1m", "\033[0m"
    DERROR_EXC = '{"output_code":"exception","exc_trace":"vars.downloadError"}'
    

class SW_DLT:

    def __init__(self, file_id, *args):
        # args[0]: media URL to download
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
            "cookiesfrombrowser": ("safari",)
        }

        processes = {
            "-v": self.single_video,
            "-a": self.single_audio,
            "-p": self.playlist_download,
            "-g": self.gallery_download
        }
        self.run = processes[args[1]]
        self.video_res = ""
        self.video_fps = ""
        self.playlist_type = ""
        self.gallery_range = ""

        if len(args) > 2:
            self.video_res = args[2] if args[1] == "-v" else ""
            self.playlist_type = args[2] if args[1] == "-p" else ""
            self.gallery_range = args[2].replace('"','').replace("'","") if args[1] == "-g" else ""

        if len(args) > 3:
            self.video_fps = args[3]  

    @staticmethod
    def update_check():
        current_time = datetime.datetime.today()
        show_progress("util", 0, 2)
        if not os.path.exists(f"{os.environ['HOME']}/Library/Cookies/Cookies.binarycookies"):
            cookie_expiration = current_time.replace(year=current_time.year + 1)
            set_cookie = f"echo 'document.cookie = \"installed=1; expires={cookie_expiration.strftime('%a, %#d %b %Y %H:%M:%S UTC')}; sameSite=Lax\";' | jsi"
            subprocess.run(set_cookie)

        #We need to wait for delay in jsi command
        while not os.path.exists(f"{os.environ['HOME']}/Library/Cookies/Cookies.binarycookies"):
            subprocess.run("sleep 1")
        
        show_progress("util", 1, 2)

        with open(f"{os.environ['HOME']}/Documents/SW-DLT/shortcut_update_ts.txt", 'r') as ts_file:
            last_check = int(ts_file.read())
    
        if int(current_time.timestamp()) - last_check < 600:
            subprocess.run("pip install chardet requests certifi mutagen -q --disable-pip-version-check --upgrade")
            subprocess.run("pip install yt-dlp yt-dlp-ejs yt-dlp-apple-webkit-jsi gallery-dl -q --disable-pip-version-check --upgrade")
            #yt-dlp is reloaded here to avoid issues after updates
            importlib.reload(yt_dlp)
        
        show_progress("util", 2, 2)

    def single_video(self):
        default_format = "best/bestvideo+bestaudio"
        custom_format = ""\
            "bestvideo[height={0}][fps<={1}]+bestaudio/"\
            "best[height={0}][fps<={1}]/"\
            "bestvideo[height<={0}][fps<={1}]+bestaudio/"\
            "best[height<={0}][fps<={1}]"\
            "best[height={0}]".format(self.video_res, self.video_fps)

        dl_options = {
            "format": default_format if self.video_res == "-d" else custom_format,
            "playlist_items": "1-1",
            "outtmpl": f'{self.file_id}.%(ext)s',
            "format_sort": ["res", "ext:mp4:m4a", "codec:avc:m4a"],
            **self.ytdlp_globals
        }

        try:
            # Returns shortcuts redirect URL with downloaded file data, any exception is re-thrown
            return self.single_download(dl_options)

        except (yt_dlp.utils.DownloadError, OSError) as ex:
            raise Exception(ex.args[0])

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

        except (yt_dlp.utils.DownloadError, OSError) as ex:
            raise Exception(ex.args[0])

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
                    "file_name": os.path.abspath(file),
                    "file_title": vid_title
                }
                return f'shortcuts://run-shortcut?name=SW-DLT&input=text&text={urllib.parse.quote(json.dumps(output))}'
        # If for some reason the above doesn't find the downloaded file, we raise generic Exception
        raise Exception(Consts.DERROR)

    def gallery_download(self):
        try:
            # Creating temp folder to store media
            os.makedirs(self.file_id, exist_ok=True)
            dl_cmd = "gallery-dl {0} --range \"{1}\" --directory {2} --cookies-from-browser safari".format(
                self.media_url, self.gallery_range, self.file_id)
                
            with subprocess.Popen(dl_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=1, universal_newlines=True) as gdl:
                for entry in gdl.stdout:
                    show_progress("manual", 1, 1)        
                
            files = os.listdir(self.file_id)
            # No files returned, raises Exception
            if len(files) == 0:
                raise OSError()

            # Single item, directly outputs the item
            elif len(files) < 2:
                file = "{0}/{1}".format(self.file_id, files[0])
                output = {
                    "output_code": "success",
                    "file_name": os.path.abspath(file),
                    "file_title": self.date_id
                }

            # Mutiple items, zips temp folder and returns it
            else:
                shutil.make_archive(self.file_id, "zip", self.file_id)
                output = {
                    "output_code": "success",
                    "file_name": os.path.abspath(self.file_id + ".zip"),
                    "file_title": self.date_id
                }

            return f'shortcuts://run-shortcut?name=SW-DLT&input=text&text={urllib.parse.quote(json.dumps(output))}'
        except subprocess.CalledProcessError as ex:
            clean_stderr = ex.output.decode("utf-8").rstrip()
            raise Exception(clean_stderr)
        except (AttributeError, OSError) as ex2:
            raise Exception(Consts.DERROR_EXC)
            
    def playlist_download(self):
        dl_options = {
            "format": "best" if self.playlist_type == "-v" else "bestaudio[ext*=4]/bestaudio[ext=mp3]/best[ext=mp4]/best",
            "postprocessors": [] if self.playlist_type == "-v" else [{"key": "FFmpegExtractAudio", "preferredcodec": "m4a"}],
            "outtmpl": f'{self.file_id}/%(title)s.%(ext)s',
            "format_sort": ["+codec:avc:m4a"],
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
                "file_name": os.path.abspath(self.file_id + ".zip"),
                "file_title": pl_title
            }
            return f'shortcuts://run-shortcut?name=SW-DLT&input=text&text={urllib.parse.quote(json.dumps(output))}'

        except (yt_dlp.utils.DownloadError, OSError) as ex:
            raise Exception(ex.args[0])


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
        "update_check": f'{Consts.CBLUE}Preparing{Consts.ENDL}\n{Consts.CYELLOW}Checking for Updates{Consts.ENDL}'
    }
    try:
        globals()["yt_dlp"] = __import__("yt_dlp")
        # Hashes all arguments to generate unique ID
        file_id = "SW_DLT_DL_{}".format(hashlib.md5(
            str(sys.argv).encode("utf-8")).hexdigest()[0:20])

        sw_dlt_inst = SW_DLT(file_id, *sys.argv[1:])
        header = f'{Consts.SBOLD}SW-DLT{Consts.ENDL}'

        # Pre-download check and cleanup
        subprocess.run("clear && hideKeyboard", shell=True)
        
        print(header)
        print(info_msgs["update_check"])            
        sw_dlt_inst.update_check()
        
        # If the same partial file is not found, deletes all leftovers (important)
        for file in os.listdir():
            if file.startswith("SW_DLT_DL_") and not file.startswith(file_id):
                if os.path.isdir(file):
                    shutil.rmtree(file)
                    continue
                os.remove(file)
            elif file.startswith(file_id):
                header = f'{Consts.SBOLD}SW-DLT (Resuming Download){Consts.ENDL}'

        subprocess.run("clear")
        print(header)
        print(info_msgs[sys.argv[2]])
        
        with open('SW_DLT_DL_metadata.json', 'w') as metadata:
            args = ' '.join(map(str, sys.argv[2:]))
            json.dump({f"{sys.argv[1]}": args}, metadata)
        
        return sw_dlt_inst.run()

    except Exception as exc_url:
        # All raised exceptions are handled here and send the user back to the shortcut with a message
        if str(exc_url.args[0]) not in [Consts.DERROR_EXC]:
            b64_err = base64.b64encode(exc_url.args[0].encode()).decode()
            UNK_EXC = '{{"output_code":"exception","exc_trace":"{0}"}}'.format(b64_err)
            return f'shortcuts://run-shortcut?name=SW-DLT&input=text&text={urllib.parse.quote(UNK_EXC)}'
        return f'shortcuts://run-shortcut?name=SW-DLT&input=text&text={urllib.parse.quote(str(exc_url.args[0]))}'


if __name__ == "__main__":
    subprocess.run("open " + main())
    