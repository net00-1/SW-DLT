import youtube_dl
import subprocess
import shutil

#SW-DLT Playlist Download Script

#Get formats for downloading playlist audio or video

userOpts = {"format":"pFormat","outtmpl":"SWDLTMultipleDL/%(title)s.%(ext)s","fixup":"never"}
mediaURL = 'mediaURL'

#Download either audio or video playlist

with youtube_dl.YoutubeDL(userOpts) as vidObj:
	vidObj.download([mediaURL])

#Zip playlist items into container, remove leftover directory

shutil.make_archive("SWDLTMultipleDL","zip","SWDLTMultipleDL")

subprocess.run("rm -r -f SWDLTMultipleDL")
