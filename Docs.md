# SW-DLT: Documentation

Detailed information about all the features available on SW-DLT. This information is not included in the RoutineHub page for sake of simplicity.

## Single Video Download

The video download option offers two types of downloads: Default and Custom Quality. Videos are saved with the original titles fetched by `yt-dlp`. Both options prioritize iOS natively playable codecs with a priority of `+codec:avc:m4a`

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

## Single Audio Download

Audio downloads prioritize the best audio available from a website. In case there is no audio only stream, the best muxed video will be used to extract audio from it. Audios are saved with the original titles fetched by `yt-dlp`.

`bestaudio[ext*=4]/bestaudio[ext=mp3]/best[ext=mp4]/best`

1. Best MP4/M4A audio available
2. Best MP3 audio available
3. Audio extracted from best MP4 video available
4. Audio extracted from best video available

## Playlist Download

Playlist downloads support both downloading all items in the playlist as videos or as audio only files. There are no quality options for video playlist downloads currently. Audio playlist downlods can use FFmpeg to correct errors and to extract audio from videos. Playlists are saved with the original titles fetched by `yt-dlp`. Both options prioritize iOS natively playable codec with a priority of `+codec:avc:m4a`

Video downloads use the formats: `best[ext=mp4]/best`

1. Best MP4 video
2. Best video of any type

Audio downloads use the formats `bestaudio[ext*=4]/bestaudio[ext=mp3]/best[ext=mp4]/best`

1. Best MP4/M4A audio available
2. Best MP3 audio available
3. Audio extracted from best MP4 video available
4. Audio extracted from best video available

## Gallery Download

Gallery downloads are done using `gallery-dl` instead of `yt-dlp`. `gallery-dl` works primarily with images, but can be used to download GIFs and Clips from social media and other hosting websites. `gallery-dl` is able to download items in bulk up to entire websites and user feeds. 

Single item downloads with `gallery-dl` are returned as-is, while multi-item downloads are packaged in a zip archive. Due to lack of proper python API, items are given timestamp names.

Gallery downloading supports custom download ranges (which are directly passed to `gallery-dl`). 

Example: `1, 2-5, 7, 9-15`

- Downloads the first item, followed by items 2 to 5, followed by item 7, followed by items 9 to 15
- The first item is usually the newest item in a social media feed

## Authentication

`yt-dlp` and `gallery-dl` are automatically set to use cookies for authentication. This allows for downloading of media that is restricted behind a login page. Use the following steps per authenticated website:

1. Open the a-Shell or a-Shell Mini app
2. Enter command `internalbrowser` followed by the website URL you want to access. For instance, `internalbrowser https://instagram.com`. 
3. A Web View of the website should open within the terminal. In case nothing happens, make sure to include `https://` in the previous step.
4. Navigate to the login screen of the website and login as you would usually do.
5. Once you have logged in, swipe from the left until you are back at the terminal screen. Alternatively, you can simply go into the App Switcher and swipe a-Shell away.

**NOTE:** SW-DLT does not access credentials or cookie data. `yt-dlp` and `gallery-dl` use it directly.

## Saving Downloads

Downloads are NOT automatically saved by SW-DLT due to the many different file types that are supported. All downloads are shown to the user using the share sheet preview. From this preview users are able to choose where to send the downloaded item(s).

It is recommended to have the VLC app or another universal media player app to enable playing media on unsupported formats for iOS/iPadOS.

## Resuming Downloads

Resuming a download only works if you retry the **LAST** attempted download with the **EXACT** same parameters (URL, quality, type, authentication type, etc). You can verify that a download is resuming if you see "SW-DLT (Resuming Download)" as the header in a-Shell when the program is running. You can stop and resume the same
download as many times as needed, but **if you download something else before completing the partial download, the partial files will be removed**. This ensures no accumulation of more than one partial files in the `$HOME/Documents/SW-DLT` directory. Resuming downloads works with ALL functions of the shortcut.

Example:
- If you attempted to download video X but interrupted the download, and then you attempt to download video X again, it will be resumed (if the same parameters are used).
- If you attempted to download video X but interrupted the download, **but then you attempt to download video Y**, the files for video X will be cleaned (at this point
video Y will take the place as the video that can be resumed if it's interrupted).