import urllib.parse
import subprocess
import hashlib
import base64


class Consts:
    CYELLOW, CGREEN, CBLUE, SBOLD, ENDL = "\033[93m", "\033[92m", "\033[94m", "\033[1m", "\033[0m"
    NO_TICKET_ERROR = '{"output_code":"exception","exc_trace":"No download ticket was found, please report this issue within the About section."}'
    INVALID_TICKET_ERROR = '{"output_code":"exception","exc_trace":"The ticket could not be parsed properly, please report this issue within the About section"}'
    NO_MODULE_ERROR = '{"output_code":"exception","exc_trace":"Could not find yt-dlp installation, please follow steps to reinstall SW-DLT"}'

class InvalidTicketError(Exception):
    # Sends back to the Shortcuts app if the ticket cannot be parsed correctly
    def __init__(self, msg):
        self.msg = msg
        super().__init__(self.msg)


class SW_DLT:
    def __init__(self, ticket):
        self.parse_ticket(ticket)
        self.download_id = "SW_DLT_DL_{}".format(hashlib.md5(str(ticket).encode("utf-8")).hexdigest()[0:20])

    def parse_ticket(ticket):
        print('something')
        raise InvalidTicketError


def main():
    info_msgs = {
        "video": f'{Consts.CBLUE}Video Download{Consts.ENDL}\n{Consts.CYELLOW}Custom qualities require processing{Consts.ENDL}',
        "audio": f'{Consts.CBLUE}Audio Download{Consts.ENDL}\n{Consts.CYELLOW}Sometimes audio processing is needed{Consts.ENDL}',
        "video_playlist": f'{Consts.CBLUE}Video Playlist Download{Consts.ENDL}\n{Consts.CYELLOW}Process time depends on playlist length{Consts.ENDL}',
        "audio_playlist": f'{Consts.CBLUE}Audio Playlist Download{Consts.ENDL}\n{Consts.CYELLOW}Process time depends on playlist length{Consts.ENDL}',
        "gallery": f'{Consts.CBLUE}Gallery Download{Consts.ENDL}\n{Consts.CYELLOW}Process time depends on collection length{Consts.ENDL}',
        "update_check": f'{Consts.CBLUE}Preparing{Consts.ENDL}\n{Consts.CYELLOW}Checking for Updates{Consts.ENDL}'
    }

    try:
        # Global yt-dlp module variable which we can reload later
        globals()['yt_dlp'] = __import__('yt_dlp')

        with open('SW_DLT_DL_ticket.json', 'r') as ticket_file:
            ticket = ticket_file.read()
        sw_dlt = SW_DLT(ticket)

    except ModuleNotFoundError as err:
        return_url = f'shortcuts://run-shortcut?name=SW-DLT&input=text&text{urllib.parse.quote(Consts.NO_MODULE_ERROR)}'
    except FileNotFoundError as err:
        return_url = f'shortcuts://run-shortcut?name=SW-DLT&input=text&text{urllib.parse.quote(Consts.NO_TICKET_ERROR)}'
    except InvalidTicketError as err:
        return_url = f'shortcuts://run-shortcut?name=SW-DLT&input=text&text{urllib.parse.quote(Consts.INVALID_TICKET_ERROR)}'
    finally:
        print(f'open {return_url}')



if __name__ == '__main__':
    main()