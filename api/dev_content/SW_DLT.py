import urllib.parse
import subprocess
import importlib
import datetime
import hashlib
import base64
import shutil
import json
import os


class Consts:
    CYELLOW, CGREEN, CBLUE, SBOLD, ENDL = "\033[93m", "\033[92m", "\033[94m", "\033[1m", "\033[0m"
    NO_FILE_ERROR = '{"output_code":"exception","exc_trace":"Unable to find startup files, cannot continue. Please report this issue within the About section"}'
    INVALID_TICKET_ERROR = '{"output_code":"exception","exc_trace":"The ticket could not be verified properly, please report this issue within the About section"}'
    NO_MODULE_ERROR = '{"output_code":"exception","exc_trace":"Could not find yt-dlp installation, please follow top comment steps (within Shortcuts) to reinstall SW-DLT"}'
    DL_FINISHED_NO_FILE = 'yt-dlp exited successfully but no media file(s) were found'


class InvalidTicketError(Exception):
    # Sends back to the Shortcuts app if the ticket cannot be verified correctly
    def __init__(self, msg):
        self.msg = msg
        super().__init__(self.msg)


class SW_DLT:
    def __init__(self, ticket):
        self.ticket = ticket
        self.verify_ticket(ticket)
        if ticket['run_mode'] == 'install':
            install_setup()
            return

        # Main instance vars
        self.download_id = 'SW_DLT_DL_{}'.format(hashlib.md5(str(ticket).encode('utf-8')).hexdigest()[0:20])
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

        self.partial_download = False
        # Creating temp folder to store media & additional cleanup of left over downloads
        os.makedirs(self.download_id, exist_ok=True)
        for file in os.listdir():
            if file.startswith("SW_DLT_DL_") and not file.startswith(self.download_id):
                if os.path.isdir(file):
                    shutil.rmtree(file)
                    continue
                os.remove(file)
            elif file.startswith(self.download_id):
                self.partial_download = True

        self.download = ticket['type']

    def verify_ticket(self, ticket):
        try:
            if ticket['run_mode'] is None or ticket['release_name'] is None or ticket['logging'] is None:
                # This checks basic ticket values, if it lacka any we use defaults to launch user back to shortcut
                ticket['release_name'] = 'SW-DLT'
                raise ValueError()
            if ticket['run_mode'] == 'install':
                return # We stop validating here if the ticket requests installation.

            if ticket['type'] not in ('gallery', 'video', 'audio') or ticket['url'] is None:
                raise ValueError()

            if ticket['type'] == 'video':
                if ticket['video_args'] is None:
                    raise ValueError()
                if ticket['video_args']['res'] is None or ticket['video_args']['subtitles'] is None:
                    raise ValueError()
                if ticket['video_args']['res'] != 'default' and ticket['video_args']['fps'] not in ('30', '60'):
                    raise ValueError()

            if ticket['type'] == 'gallery':
                if ticket['gallery_args'] is None:
                    raise ValueError()
                if ticket['gallery_args']['range'] is None:
                    raise ValueError()

        except ValueError as err:
            raise InvalidTicketError(None)

    def packaging(self):
        raw_files = os.listdir(self.download_id)
        # No files returned, raises Exception
        if len(raw_files) == 0: 
            raise OSError(Consts.DL_FINISHED_NO_FILE)
        elif len(raw_files) < 2:
            # We do manual overwrite of file name (even if it has title), this is due to the title insertion being done in the shortcut output handler
            discard_name, ext = os.path.splitext(raw_files[0])
            safe_file_name = f'{0}/{1}{2}'.format(self.download_id, self.download_id, ext)
            target_file = f'{0}/{1}'.format(self.download_id, raw_files[0])
            os.rename(target_file, safe_file_name)
            return os.path.abspath(safe_file_name)
        else:
            shutil.make_archive(self.download_id, "zip", self.download_id)
            target_file = self.download_id + '.zip'
            return os.path.abspath(target_file)

    
    def video(self):
        default_format = 'best/bestvideo+bestaudio'
        custom_format = ''\
            'bestvideo[height={0}][fps<={1}]+bestaudio/'\
            'best[height={0}][fps<={1}]/'\
            'bestvideo[height<={0}][fps<={1}]+bestaudio/'\
            'best[height<={0}][fps<={1}]'\
            'best[height={0}]'.format(self.ticket['video_args']['res'], self.ticket['video_args']['fps'])

        dl_options = {
            'format': default_format if self.ticket['video_args']['res'] == 'default' else custom_format,
            'outtmpl': f'{self.download_id}/%(title)s.%(ext)s',
            'format_sort': ['res', 'ext:mp4:m4a', 'codec:avc:m4a'],
            **self.ytdlp_globals
        }

        try:
            # Returns shortcuts redirect URL with downloaded file data, any exception is re-thrown
            with yt_dlp.YoutubeDL(dl_options) as dl_obj:
                meta_data = dl_obj.extract_info(self.ticket['url'], download=False)
                dl_title = meta_data.get('title', self.date_id)
                dl_obj.download([self.ticket['url']])

            pkg_path = self.packaging()
            output = {
                'output_code': 'success',
                'file_name': pkg_path,
                'file_title': dl_title
            }
            return f'shortcuts://run-shortcut?name={self.ticket['release_name']}&input=text&text={urllib.parse.quote(json.dumps(output))}'

        except (yt_dlp.utils.DownloadError, OSError) as ex:
            raise Exception(ex.args[0])

    def audio(self):
        dl_options = {
            "format": "bestaudio[ext*=4]/bestaudio[ext=mp3]/best[ext=mp4]/best",
            "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "m4a"}],
            "outtmpl": f'{self.download_id}/%(title)s.%(ext)s',
            **self.ytdlp_globals
        }

        try:
            # Returns shortcuts redirect URL with downloaded file data, any exception is re-thrown
            with yt_dlp.YoutubeDL(dl_options) as dl_obj:
                meta_data = dl_obj.extract_info(self.ticket['url'], download=False)
                dl_title = meta_data.get('title', self.date_id)
                dl_obj.download([self.ticket['url']])

            pkg_path = self.packaging()
            output = {
                'output_code': 'success',
                'file_name': pkg_path,
                'file_title': dl_title
            }
            return f'shortcuts://run-shortcut?name={self.ticket['release_name']}&input=text&text={urllib.parse.quote(json.dumps(output))}'

        except (yt_dlp.utils.DownloadError, OSError) as ex:
            raise Exception(ex.args[0])

    def gallery(self):
        pass

def show_progress(data_stream, curr=0, total=0):
    # data_stream is the type of data received, allowed values: manual (for gallery-dl downloads), util (for utility processes)
    # It can also be yt-dlp download data streams
    if data_stream == 'manual':
        if curr != total:
            print(
                f'\rDownloading: {Consts.CYELLOW}{curr/total:.1%}{Consts.ENDL}', end='')
            return
        print(f'\x1b[1K\r{Consts.CGREEN}Downloaded{Consts.ENDL}')
    elif data_stream == 'util':
        print(
            f'\rLoading: {Consts.CYELLOW}{curr/total:.1%}{Consts.ENDL}', end='')
        return
    else:
        if data_stream['status'] == 'downloading':
            print(
                f'\rDownloading: {Consts.CYELLOW}{data_stream['_percent_str'].strip()}{Consts.ENDL}', end='')
        elif data_stream['status'] == 'finished':
            print(f'\x1b[1K\r{Consts.CGREEN}Downloaded{Consts.ENDL}')
    return


def format_processing(process_stream):
    if process_stream['status'] == 'started':
        print(f'\r{Consts.CYELLOW}Processing{Consts.ENDL}', end='')
    elif process_stream['status'] == 'finished':
        print(f'\x1b[1K\r{Consts.CGREEN}Processed{Consts.ENDL}')
    return


def install_setup():
    print("Installing. Please wait...")

    current_time = datetime.datetime.today()
    show_progress('util', 0, 2)
    if not os.path.exists(f"{os.environ['HOME']}/Library/Cookies/Cookies.binarycookies"):
        cookie_expiration = current_time.replace(year=current_time.year + 1).strftime('%a, %-d %b %Y %H:%M:%S UTC')
        set_cookie = f"echo 'document.cookie = \"installed=1; expires={cookie_expiration}; sameSite=Lax\";' | jsi"
        subprocess.run(set_cookie)

    show_progress('util', 1, 2)
    # Wait for delay in jsi command
    while not os.path.exists(f"{os.environ['HOME']}/Library/Cookies/Cookies.binarycookies"):
        subprocess.run('sleep 1')

    subprocess.run('pip install chardet requests certifi mutagen yt-dlp yt-dlp-ejs yt-dlp-apple-webkit-jsi gallery-dl -q --disable-pip-version-check --upgrade')
    show_progress('util', 2, 3)
    with open('.installed', 'w') as flag_file:
        pass

    os.remove("SW_DLT_DL_ticket.json")
    show_progress('util', 3, 3)
    

def update_check():
    current_time = datetime.datetime.today()
    show_progress('util', 0, 1)

    with open(f"{os.environ['HOME']}/Documents/SW-DLT/update_last_check.txt", 'r') as file:
        last_check = int(file.read())

    if int(current_time.timestamp()) - last_check < 600:
        subprocess.run('pip install chardet requests certifi mutagen yt-dlp yt-dlp-ejs yt-dlp-apple-webkit-jsi gallery-dl -q --disable-pip-version-check --upgrade')
        # yt-dlp is reloaded here to avoid issues from updates
        importlib.reload(yt_dlp)
    
    show_progress('util', 1, 1)


def main():
    info_msgs = {
        'video': f'{Consts.CBLUE}Video Download{Consts.ENDL}\n{Consts.CYELLOW}Custom qualities require processing{Consts.ENDL}',
        'audio': f'{Consts.CBLUE}Audio Download{Consts.ENDL}\n{Consts.CYELLOW}Sometimes audio processing is needed{Consts.ENDL}',
        'gallery': f'{Consts.CBLUE}Gallery Download{Consts.ENDL}\n{Consts.CYELLOW}Process time depends on collection length{Consts.ENDL}',
        'update_check': f'{Consts.CBLUE}Preparing{Consts.ENDL}\n{Consts.CYELLOW}Checking for Updates{Consts.ENDL}'
    }

    try:
        header = f'{Consts.SBOLD}SW-DLT{Consts.ENDL}'
        print(header)

        with open('SW_DLT_DL_ticket.json', 'r') as ticket_file:
            ticket = json.load(ticket_file)
        sw_dlt = SW_DLT(ticket)
        callback_sc = sw_dlt.ticket['release_name']

        if sw_dlt.ticket['run_mode'] == 'install':
            return_url = f"shortcuts://run-shortcut?name={callback_sc}&input=text&text={sw_dlt.ticket['url']}"
            return

        # Global yt-dlp module variable which we can reload later
        globals()['yt_dlp'] = __import__('yt_dlp')
        print(info_msgs['update_check'])            
        update_check()

        subprocess.run("clear")
        if sw_dlt.partial_download:
            header = f'{Consts.SBOLD}SW-DLT (Continuing Download){Consts.ENDL}'
        print(header)
        print(info_msgs[sw_dlt.ticket['type']])

        return_url = sw_dlt.download()

    except ModuleNotFoundError as err:
        return_url = f'shortcuts://run-shortcut?name={callback_sc}&input=text&text{urllib.parse.quote(Consts.NO_MODULE_ERROR)}'
    except FileNotFoundError as err:
        return_url = f'shortcuts://run-shortcut?name={callback_sc}&input=text&text{urllib.parse.quote(Consts.NO_FILE_ERROR)}'
    except InvalidTicketError as err:
        return_url = f'shortcuts://run-shortcut?name={callback_sc}&input=text&text{urllib.parse.quote(Consts.INVALID_TICKET_ERROR)}'
    except Exception as err:
        dl_err = (
            'The download encountered an error. Usually this is fixed by checking '
            'internet connection, verifying the download source for selected quality, or'
            'checking authentication. Check about page if issue perists. Internal tool message:\n'
            f'{err.args[0]}'
        )
        UNK_EXC = '{{"output_code":"exception","exc_trace":"{0}"}}'.format(base64.b64encode(dl_err.encode()).decode())
        return_url = f'shortcuts://run-shortcut?name={callback_sc}&input=text&text={urllib.parse.quote(UNK_EXC)}'
    finally:
        subprocess.run('open ' + return_url)


if __name__ == '__main__':
    main()
    