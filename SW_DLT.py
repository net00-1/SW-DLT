# SW-DLT main download script, do not copy without permission!

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

FFMPEG_URL = "https://github.com/holzschu/a-Shell-commands/releases/download/0.1/ffmpeg.wasm"
FFPROBE_URL = "https://github.com/holzschu/a-Shell-commands/releases/download/0.1/ffprobe.wasm"

media_url = sys.argv[1]
download_type = sys.argv[2]
out_name = datetime.datetime.today().strftime("%d-%m-%y-%H-%M-%S")


def main():
    # Pre download check & cleanup
    subprocess.run("clear")
    print("SW-DLT")
    print("Checking Dependencies...")
    check_setup()

    subprocess.run("rm -f *-*-*-*-*-*.*")
    subprocess.run("rm -r -f *-*-*-*-*-*")
    subprocess.run("clear")

    # Download functions
    if download_type == "video":
        print("Downloading video, custom qualities can take longer to process...")
        video_download()
    elif download_type == "audio":
        print("Downloading audio...")
        audio_download()
    elif download_type == "playlist":
        print("Downloading playlist, process will take longer for bigger playlists...")
        playlist_download()
    elif download_type == "gallery":
        print("Downloading URLs, process will take longer for bigger albums...")
        gallery_download()
    elif download_type == "erase":
        print("Deleting all dependencies, please wait...")
        delete_dependencies()


def check_setup():
    flag = False
    
    if "Package(s) not found" in subprocess.getoutput("pip show youtube-dl"):
        subprocess.run("pip -q install --upgrade youtube-dl")
        flag = True
    if "Package(s) not found" in subprocess.getoutput("pip show gallery-dl"):
        subprocess.run("pip -q install --upgrade gallery-dl")
        flag = True
    if flag is True:
        subprocess.run("open shortcuts://run-shortcut?name=SW-DLT&input=text&text=EXCEPTION.vars.restartRequired")
        subprocess.run("clear")
        sys.exit()
    
    subprocess.run("cd")
    if os.path.exists("./bin") is False:
        subprocess.run("mkdir bin")
        subprocess.run("cd bin")
        req1 = requests.get(FFMPEG_URL)
        with open('./ffmpeg.wasm', 'wb') as ffmpeg:
            ffmpeg.write(req1.content)
        ffmpeg.close()

        req2 = requests.get(FFPROBE_URL)
        with open('./ffprobe.wasm', 'wb') as ffprobe:
            ffprobe.write(req2.content)
        ffprobe.close()

    else:
        subprocess.run("cd bin")
        if os.path.exists("./ffprobe.wasm") is False:
            req2 = requests.get(FFPROBE_URL)
            with open('./ffprobe.wasm', 'wb') as ffprobe:
                ffprobe.write(req2.content)
            ffprobe.close()

        if os.path.exists("./ffmpeg.wasm") is False:
            req1 = requests.get(FFMPEG_URL)
            with open('./ffmpeg.wasm', 'wb') as ffmpeg:
                ffmpeg.write(req1.content)
            ffmpeg.close()

    subprocess.run("jump shortcuts")	


def delete_dependencies():
    subprocess.run("pip uninstall -y youtube-dl")
    subprocess.run("pip uninstall -y youtube-dl")
    subprocess.run("cd")
    subprocess.run("cd bin")
    subprocess.run("rm -f ffmpeg.wasm")
    subprocess.run("rm -f ffprobe.wasm")

    subprocess.run("open shortcuts://run-shortcut?name=SW-DLT&input=text&text=EXCEPTION.vars.erasedAll")


def video_download():
    video_res = sys.argv[3]
    
    if video_res == "default":
        format_opts = {"format": "best[ext=mp4]/best/bestvideo[ext=mp4]+bestaudio[ext*=4]/bestvideo[ext!*=4]+bestaudio[ext!*=4]", "playlist_items": "1-1", "outtmpl": "{}.%(ext)s".format(out_name)}
    else:
        video_fps = sys.argv[4]
        format_opts = {"format": "bestvideo[ext=mp4][height>={0}][fps>={1}]+bestaudio[ext*=4]/bestvideo[ext=mp4][height>={0}][fps<={1}]+bestaudio[ext*=4]/bestvideo[ext!*=4][height>={0}][fps>={1}]+bestaudio[ext!*=4]/bestvideo[ext!*=4][height>={0}][fps<={1}]+bestaudio[ext!*=4]/bestvideo[ext=mp4][height<={0}][fps>={1}]+bestaudio[ext*=4]/bestvideo[ext=mp4][height<={0}][fps<={1}]+bestaudio[ext*=4]/bestvideo[ext!*=4][height<={0}][fps>={1}]+bestaudio[ext!*=4]/bestvideo[ext!*=4][height<={0}][fps<={1}]+bestaudio[ext!*=4]/best[ext=mp4][height>={0}][fps>={1}]/best[ext=mp4][height>={0}][fps<={1}]/best[ext!*=4][height>={0}][fps>={1}]/best[ext!*=4][height>={0}][fps<={1}]/best[ext=mp4][height<={0}][fps>={1}]/best[ext=mp4][height<={0}][fps<={1}]/best[ext!*=4][height<={0}][fps>={1}]/best[ext!*=4][height<={0}][fps<={1}]".format(video_res, video_fps), "playlist_items": "1-1", "outtmpl": "{}.%(ext)s".format(out_name)}
    single_ytdl(format_opts)


def audio_download():
    format_opts = {"format": "bestaudio[ext*=4]/bestaudio[ext=mp3]/best[ext=mp4]/best", "playlist_items": "1-1", "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "m4a"}], "outtmpl": "{}.%(ext)s".format(out_name)}
    single_ytdl(format_opts)


def single_ytdl(format_opts):
    try:
        with youtube_dl.YoutubeDL(format_opts) as vidObj:
            vidObj.download([media_url])
        re_pattern = re.compile(out_name + "\.[\w]{2,4}")
        file_name = re_pattern.match(subprocess.getoutput("ls")).group(0)
        subprocess.run("open shortcuts://run-shortcut?name=SW-DLT&input=text&text=OUTPUT.{}".format(file_name))

    except:
        subprocess.run("open shortcuts://run-shortcut?name=SW-DLT&input=text&text=EXCEPTION.vars.downloadError")
        subprocess.run("clear")
        sys.exit()


def gallery_download():
    gallery_range = sys.argv[3]
    gallery_urls = None

    if gallery_range == "all":
        gallery_urls = subprocess.getoutput("gallery-dl -G {}".format(media_url)).splitlines()
    else:
        gallery_urls = subprocess.getoutput("gallery-dl -G {0} --range '{1}'".format(media_url, gallery_range)).splitlines()

    img_count = 0
    ext = ""

    subprocess.run("mkdir {}".format(out_name))
    subprocess.run("cd {}".format(out_name))

    for url in gallery_urls:
        if url.startswith("http"):
            img_get = requests.get(str(url))
            c_type = img_get.headers['content-type']
            ext = mimetypes.guess_extension(c_type)

            img_count = img_count + 1
            with open('IMG_{0}{1}'.format(img_count, ext), 'wb') as img:
                img.write(img_get.content)
            img.close()

    if img_count < 1:
        subprocess.run("open shortcuts://run-shortcut?name=SW-DLT&input=text&text=EXCEPTION.vars.downloadError")
        subprocess.run("jump shortcuts")
        subprocess.run("rm -r -f {}".format(out_name))
        sys.exit()
    elif img_count < 2:
        subprocess.run("mv {0} $SHORTCUTS/{1}".format("IMG_" + str(img_count) + ext, out_name + ext))
        subprocess.run("rm -r -f {}".format(out_name))
        subprocess.run("open shortcuts://run-shortcut?name=SW-DLT&input=text&text=OUTPUT.{}".format(out_name + ext))
    else:
        subprocess.run("jump shortcuts")
        shutil.make_archive(out_name, "zip", out_name)
        subprocess.run("rm -r -f {}".format(out_name))
        subprocess.run("open shortcuts://run-shortcut?name=SW-DLT&input=text&text=OUTPUT.{}".format(out_name + ".zip"))


def playlist_download():
    playlist_type = sys.argv[3]
    format_opts = None

    if playlist_type == "video":
        format_opts = {"format": "best[ext=mp4]/best", "outtmpl": "{}/%(title)s.%(ext)s".format(out_name)}
    else:
        format_opts = {"format": "bestaudio[ext*=4]/bestaudio[ext=mp3]/best[ext=mp4]/best", "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "m4a"}], "outtmpl": "{}/%(title)s.%(ext)s".format(out_name)}

    try:
        with youtube_dl.YoutubeDL(format_opts) as vidObj:
            vidObj.download([media_url])
        shutil.make_archive(out_name, "zip", out_name)
        subprocess.run("rm -r -f {}".format(out_name))
        subprocess.run("open shortcuts://run-shortcut?name=SW-DLT&input=text&text=OUTPUT.{}".format(out_name + ".zip"))

    except:
        subprocess.run("open shortcuts://run-shortcut?name=SW-DLT&input=text&text=EXCEPTION.vars.downloadError")
        subprocess.run("clear")
        sys.exit()


if __name__ == "__main__":
    main()
