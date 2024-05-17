# SW-DLT: Documentation

Detailed information about all the features available on SW-DLT. This information is not included in the RoutineHub page to save space and for simplicity.

## Video Downloading

The video download option offers two types of downloads: Default and Custom Quality. Videos are saved with the proper titles available from `yt-dlp`. Both options prioritize iOS natively playable codec with a priority of `+codec:avc:m4a`

**Default Quality**: videos are downloaded using the following `yt-dlp` format string:

 `best/bestvideo+bestaudio` i.e:

1. Best quality available (video and audio stream)
2. Best quality available (separate video and audio to merge with FFmpeg)

The default quality is the most reliable way to download videos from websites that might not return media format data to `yt-dlp` or are not in the list of supported websites and need to be downloaded using `yt-dlp`'s generic extractor. This option also mostly avoids using FFmpeg to save battery life (FFmpeg can still be used to correct file issues).

**Custom Quality**: Custom quality videos are selected based on the `height` of the video image that corresponds to the "quality" selected by the user, and the `fps` chosen.

The priority of videos to search is as follows:

1. `bestvideo[height=X][fps<=Y]+bestaudio`  (Exact resolution, closest FPS, unmerged)
2. `bestvideo[height<=X][fps<=Y]+bestaudio` (Closest resolution, closest FPS, unmerged)
3. `best[height=X][fps<=Y]`                 (Exact resolution, closest FPS, merged)
4. `best[height<=X][fps<=Y]`                (Closest resolution, closest FPS, merged)

Unmerged options are prioritized, so what user choices are not ignored, since websites tend to offer more resolution and FPS media options on separate video and audio files.

## Audio Downloading

Audio downloads prioritize the best audio available from a website. In case there is no audio only stream, the best muxed video will be used to extract audio from it. Audio downloads are also saved with the proper title from `yt-dlp`.

`bestaudio[ext*=4]/bestaudio[ext=mp3]/best[ext=mp4]/best`

1. Best MP4/M4A audio available
2. Best MP3 audio available
3. Audio extracted from best MP4 video available
4. Audio extracted from best video available

## Playlist Downloading

Playlist downloads support both downloading all items in the playlist as videos or as audio only files. There are no quality options for video playlist downloads currently. Audio playlist downlods can use FFmpeg to correct errors and to extract audio from videos. Playlists are saved with the proper titles availale from `yt-dlp`. Both options prioritize iOS natively playable codec with a priority of `+codec:avc:m4a`

Video downloads use the formats: `best[ext=mp4]/best`

1. Best MP4 video
2. Best video of any type

Audio downloads use the formats `bestaudio[ext*=4]/bestaudio[ext=mp3]/best[ext=mp4]/best`

1. Best MP4/M4A audio available
2. Best MP3 audio available
3. Audio extracted from best MP4 video available
4. Audio extracted from best video available

## Gallery Downloading

Gallery downloads are done using `gallery-dl` instead of `yt-dlp`. `gallery-dl` works primarily with images, but can be used to download GIFs and Clips from social media and other hosting websites. `gallery-dl` is able to download items in bulk up to entire websites and user profiles. 

Single item downloads with `gallery-dl` are returned as-is, while multi item downloads are packaged in a zip archive. Since `gallery-dl` is not directly used to download items, there is no proper item naming available. Items are given generic names (with zip archives using the current date).

Gallery downloading supports custom download ranges (which are directly passed to `gallery-dl`). 

Example: `1, 2-5, 7, 9-15`

- Downloads the first item, followed by items 2 to 5, followed by item 7, followed by items 9 to 15
- The first item is usually the newest item in a social media page

## Authentication

SW-DLT **does NOT** handle user credentials due to lack of proper mechanisms to do so in Shortcuts. It's possible, however, to use built-in authentication features from gallery-dl and yt-dlp:

**Gallery-dl**

A gallery-dl configuration file can be stored at `$XDG_CONFIG_HOME/gallery-dl/config.json`. Credentials for multiple supported websites can be added here in the following format:

```json
{
    "extractor": {
        "twitter": {
            "username": "<USER/EMAIL>",
            "password": "<PASS>"
        },
        "instagram": {
            "cookies": "path/to/cookies.txt"
        }
    }
}
```
For more information, visit the gallery-dl [documentation](https://github.com/mikf/gallery-dl#username--password).

**yt-dlp**

A yt-dlp [configuration file](https://github.com/yt-dlp/yt-dlp#configuration) can be stored at `$XDG_CONFIG_HOME/yt-dlp/config`. Within this file you can store global yt-dlp options. For authentication, add the `--netrc` flag to this file:

```
# Enabling netrc
--netrc

# Optional: specify location of .netrc file
--netrc-location <PATH>
```

Next, create a [`.netrc` file](https://github.com/yt-dlp/yt-dlp#configuration) in your home directory, or the directory specified in `--netrc-location` containing the credentials per website:

```
machine <website> login <username> password <password>
```

## Saving Downloaded Media

Downloads are NOT automatically saved by SW-DLT due to the many different file types that are supported. All downloads are shown to the user using the share sheet preview. From this preview users are able to choose where to send the downloaded item(s).

It is recommended to have the VLC app or another universal media player app to enable playing media on unsupported formats for iOS/iPadOS.

## Updating Utilities

In order to update the utilities used by SW-DLT, you must first use the `deleteAll` toggle inside the shortcuts editor screen. Set it to `true` and run the shortcut (& accept the warning). Once the process finishes, set the toggle back to `false`.

This option is used to uninstall all the utilities without having to delete the a-Shell app. The next time a download is requested after deletion, the most recent versions of all the utilities will be installed.

## Resuming Downloads

Resuming a download only works if you retry the **LAST** attempted download with the **EXACT** same parameters (URL, quality, type, authentication type, etc). You can verify that a download is resuming if you see "SW-DLT (Resuming Download)" as the header in a-Shell when the program is running. You can stop and resume the same
download as many times as needed, but **if you download something else before completing the partial download, the partial files will be removed**. This ensures no accumulation of more than one partial files in the `$SHORTCUTS` directory. Resuming downloads works with ALL functions of the shortcut.

Example:
- If you attempted to download video X but interrupted the download, and then you attempt to download video X again, it will be resumed (if the same parameters are used).
- If you attempted to download video X but interrupted the download, **but then you attempt to download video Y**, the files for video X will be cleaned (at this point
video Y will take the place as the video that can be resumed if it's interrupted).

## Using Native FFmpeg
Native FFmpeg will be automatically used if you have the latest version of the a-Shell/a-Shell Mini app that ships with it included. In this case any WebAssembly version of FFmpeg  present will be deleted to avoid using it (when both versions are installed the WebAssembly version takes precedence). For older versions of a-Shell, the WebAssembly version will  be automatically installed and used. From the user side, this will be completely automatic.

## Choosing a-Shell App Version

SW-DLT supports both the a-Shell and a-Shell Mini apps. The `isMini` toggle inside the shortcut editor screen allows you to choose which app to use depending on which app is installed.

-  True = uses a-Shell Mini
-  False = uses a-Shell (full)
