import forkData (pyModule)
import subprocess
import shutil

#SW-DLT Playlist Download Script

#Get formats for downloading playlist audio or video

userOpts = {"format":"pFormat","outtmpl":"SWDLTMultipleDL/%(title)s.%(ext)s","fixup":"ffmPolicy"}
mediaURL = 'mediaURL'

#Download either audio or video playlist

with forkData (pyModule).YoutubeDL(userOpts) as vidObj:
	vidObj.download([mediaURL])

#Zip playlist items into container, remove leftover directory

shutil.make_archive("SWDLTMultipleDL","zip","SWDLTMultipleDL")

subprocess.run("rm -r -f SWDLTMultipleDL")

#Return to SWDLT with a specific function code

subprocess.run("fStart")
subprocess.run("exit")
