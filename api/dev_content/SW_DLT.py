import urllib.parse
import subprocess
import importlib
import datetime
import hashlib
import base64
import json
import os


class Consts:
    CYELLOW, CGREEN, CBLUE, SBOLD, ENDL = "\033[93m", "\033[92m", "\033[94m", "\033[1m", "\033[0m"
    NO_FILE_ERROR = '{"output_code":"exception","exc_trace":"Unable to find startup files, cannot continue. Please report this issue within the About section"}'
    INVALID_TICKET_ERROR = '{"output_code":"exception","exc_trace":"The ticket could not be verified properly, please report this issue within the About section"}'
    NO_MODULE_ERROR = '{"output_code":"exception","exc_trace":"Could not find yt-dlp installation, please follow top comment steps (within Shortcuts) to reinstall SW-DLT"}'


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

        self.download_id = 'SW_DLT_DL_{}'.format(hashlib.md5(str(ticket).encode('utf-8')).hexdigest()[0:20])

    def verify_ticket(self, ticket):
        try:
            if ticket['run_mode'] is None:
                raise ValueError()
            if ticket['run_mode'] == 'install':
                return # We stop validating here if the ticket requests installation.

        except ValueError as err:
            raise InvalidTicketError()


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

    # Wait for delay in jsi command
    while not os.path.exists(f"{os.environ['HOME']}/Library/Cookies/Cookies.binarycookies"):
        subprocess.run('sleep 1')

    subprocess.run('pip install chardet requests certifi mutagen yt-dlp yt-dlp-ejs yt-dlp-apple-webkit-jsi gallery-dl -q --disable-pip-version-check --upgrade')

    with open('.installed', 'w') as flag_file:
        pass

    os.remove("SW_DLT_DL_ticket.json")
    

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
        # Global yt-dlp module variable which we can reload later
        globals()['yt_dlp'] = __import__('yt_dlp')

        header = f'{Consts.SBOLD}SW-DLT{Consts.ENDL}'
        print(header)

        with open('SW_DLT_DL_ticket.json', 'r') as ticket_file:
            ticket = json.load(ticket_file)
        sw_dlt = SW_DLT(ticket)
        callback_sc = sw_dlt.ticket.release_name

        if sw_dlt.ticket['run_mode'] == 'install':
            return_url = f'shortcuts://run-shortcut?name={callback_sc}'
            return

        print(info_msgs['update_check'])            
        update_check()

    except ModuleNotFoundError as err:
        return_url = f'shortcuts://run-shortcut?name={callback_sc}&input=text&text{urllib.parse.quote(Consts.NO_MODULE_ERROR)}'
    except FileNotFoundError as err:
        return_url = f'shortcuts://run-shortcut?name={callback_sc}&input=text&text{urllib.parse.quote(Consts.NO_FILE_ERROR)}'
    except InvalidTicketError as err:
        return_url = f'shortcuts://run-shortcut?name={callback_sc}&input=text&text{urllib.parse.quote(Consts.INVALID_TICKET_ERROR)}'
    finally:
        print(f'open {return_url}')


if __name__ == '__main__':
    main()
    