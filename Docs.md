# SW-DLT: Documentation

Detailed information about all the features available on SW-DLT. This information is not included in the RoutineHub page to save space and for simplicity.

## Video Downloading

The video download option offers two types of downloads: Default and Custom Quality. Videos are saved with the proper titles available from youtube-dl.

**Default Quality**: videos are downloading using the following youtube-dl format string:

 `best[ext=mp4]/best/bestvideo[ext=mp4]+bestaudio[ext*=4]/bestvideo[ext!*=4]+bestaudio[ext!*=4]` i.e:

1. Best quality available with extension MP4 (video and audio stream)
2. Best quality available with any extension (video and audio stream)
3. Best quality available with extension MP4 (separate video and audio to merge with FFMpeg)
4. Best quality available with any extension (separate video and audio to merge with FFMpeg)

The default quality is the most reliable way to download videos from websites that might not return resolution data to youtube-dl or are not in the list of
supported websites and need to be downloaded using youtube-dl's generic extractor. This option also mostly avoids using FFMpeg (which saves battery, and speeds up downloads).

**Custom Quality**: videos are downloaded using the closest available resolution and FPS to the user's selection. This is done to add flexibility when the exact
resolution and frame rate is not available. The priority is as follows: (Merging separate audio and video with FFMpeg will be done first, in case there are no
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

Playlist downloads support both downloading all items in the playlist as videos or as audio only files. There is no quality options for video playlist downloads due to
the slowness of FFMpeg in a-Shell, and to save battery life. Audio playlist downlods can use FFMpeg to correct errors and to extract audio from videos.

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

## Updating Utilities

In order to update the utilities used by SW-DLT, you must first use the deleteAll toggle inside the shortcuts editor screen. This option is used to uninstall all the utilities
without having to delete the a-Shell app. The next time a download is requested after deletion, the most recent versions of all the utilities will be installed.

## Choosing a-Shell App Version

SW-DLT supports both the a-Shell and a-Shell Mini apps. The isMini toggle inside the shortcut editor screen allows you to choose which app to use depending on which app 
is installed.

-  True = uses a-Shell Mini
-  False = uses a-Shell (full)
