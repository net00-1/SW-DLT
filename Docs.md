# SW-DLT: Documentation

Detailed information about all the features available on SW-DLT. This information is not included in the RoutineHub page to save space and for simplicity.

## Video Downloading

The video download option offers two types of downloads: Default and Custom Quality. Videos are saved with the proper titles available from youtube-dl.

**Default Quality**: videos are downloaded using the following youtube-dl format string:

 `best[ext=mp4]/best/bestvideo[ext=mp4]+bestaudio[ext*=4]/bestvideo[ext!*=4]+bestaudio[ext!*=4]` i.e:

1. Best quality available with extension MP4 (video and audio stream)
2. Best quality available with any extension (video and audio stream)
3. Best quality available with extension MP4 (separate video and audio to merge with FFmpeg)
4. Best quality available with any extension (separate video and audio to merge with FFmpeg)

The default quality is the most reliable way to download videos from websites that might not return resolution data to youtube-dl or are not in the list of
supported websites and need to be downloaded using youtube-dl's generic extractor. This option also mostly avoids using FFmpeg to save battery life (FFmpeg can still be used
to correct video file issues).

**Custom Quality**: videos are downloaded using the closest available resolution and FPS to the user's selection. This is done to add flexibility when the exact
resolution and frame rate is not available. The priority is as follows: (Merging separate audio and video with FFmpeg will be done first, in case there are no
separate streams available, muxed streams will be considered).

1. MP4 video with bigger than or equal FPS and resolution to user choice
2. MP4 video with bigger than or equal resolution and less than or equal FPS to user choice
3. ANY video with bigger than or equal FPS and resolution to user choice
4. ANY video with bigger than or equal resolution and less than or equal FPS to user choice
5. MP4 video with less than or equal resolution and bigger than or equal FPS to user choice
6. MP4 video with less than or equal resolution and FPS to user choice
7. ANY video with less than or equal resolution and bigger than or equal FPS to user choice
8. ANY video with less than or equal resolution and FPS to user choice

## Audio Downloading

Audio downloads prioritize the best audio available from a website. In case there is no audio only stream, the best muxed video will be used to extract audio from it.
Audio downloads are also saved with the proper title from youtube-dl.

`bestaudio[ext*=4]/bestaudio[ext=mp3]/best[ext=mp4]/best`

1. Best MP4/M4A audio available
2. Best MP3 audio available
3. Audio extracted from best MP4 video available
4. Audio extracted from best video available

## Playlist Downloading

Playlist downloads support both downloading all items in the playlist as videos or as audio only files. There are no quality options for video playlist downloads currently. 
Audio playlist downlods can use FFmpeg to correct errors and to extract audio from videos. Playlists are saved with the proper titles availale from youtube-dl.

Video downloads use the formats: `best[ext=mp4]/best`

1. Best MP4 video
2. Best video of any type

Audio downloads use the formats `bestaudio[ext*=4]/bestaudio[ext=mp3]/best[ext=mp4]/best`

1. Best MP4/M4A audio available
2. Best MP3 audio available
3. Audio extracted from best MP4 video available
4. Audio extracted from best video available

## Gallery Downloading

Gallery downloads are done using gallery-dl instead of youtube-dl. Gallery-dl works primarily with images, but can be used to download GIFs and Clips from
social media and other hosting websites. Gallery-dl is able to download items in bulk up to entire websites and user profiles. Gallery downloading supports entering user
login details to access private content. **SW-DLT is not able to save any kind of login details for security**. Single item downloads with gallery-dl are returned
as-is, while multi item downloads are packaged in a zip archive. Since gallery-dl is not directly used to download items, there is no proper item naming available.
Items are given generic names (with zip archives using the current date).

Gallery downloading supports custom download ranges (which are directly passed to gallery-dl). 

Example: `1, 2-5, 7, 9-15`

- Downloads the first item, followed by items 2 to 5, followed by item 7, followed by items 9 to 15
- The first item is usually the newest item in a social media page

## Saving Downloaded Media

Downloads are NOT automatically saved by SW-DLT due to the many different file types that are supported. All downloads are shown to the user using the share sheet
preview. From this preview users are able to choose where to send the downloaded item(s).

It is recommended to have the VLC app or another universal media player app to enable playing media on unsupported formats for iOS/iPadOS.

## Updating Utilities

In order to update the utilities used by SW-DLT, you must first use the `deleteAll` toggle inside the shortcuts editor screen. This option is used to uninstall all the utilities
without having to delete the a-Shell app. The next time a download is requested after deletion, the most recent versions of all the utilities will be installed.

## Resuming Downloads

Resuming a download only works if you retry the **LAST** attempted download with the **EXACT** same parameters (URL, quality, type, authentication type, etc).
You can verify that a download is resuming if you see "SW-DLT (Resuming Download)" as the header in a-Shell when the program is running. You can stop and resume the same
download as many times as needed, but **if you download something else before completing the partial download, the partial files will be removed**. This ensures no 
accumulation of more than one partial files in the `$SHORTCUTS` directory. Resuming downloads works with ALL functions of the shortcut.

Example:
- If you attempted to download video X but interrupted the download, and then you attempt to download video X again, it will be resumed (if the same parameters are used).
- If you attempted to download video X but interrupted the download, **but then you attempt to download video Y**, the files for video X will be cleaned (at this point
video Y will take the place as the video that can be resumed if it's interrupted).

## Using Native FFmpeg
Native FFmpeg will be automatically used if you have the latest version of the a-Shell/a-Shell Mini app that ships with it included. In this case any WebAssembly version of FFmpeg 
present will be deleted to avoid using it (when both versions are installed the WebAssembly version takes precedence). For older versions of a-Shell, the WebAssembly version will 
be automatically installed and used. From the user side, this will be completely automatic.

## Choosing a-Shell App Version

SW-DLT supports both the a-Shell and a-Shell Mini apps. The `isMini` toggle inside the shortcut editor screen allows you to choose which app to use depending on which app 
is installed.

-  True = uses a-Shell Mini
-  False = uses a-Shell (full)
