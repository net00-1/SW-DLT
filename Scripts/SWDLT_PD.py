import youtubeModule
import subprocess
import shutil
import time

#SW-DLT Playlist Download Script

mediaURL = 'mediaURL'
userOpts = {"format":"","outtmpl":"SWDLTMultipleDL/%(title)s.%(ext)s","fixup":""}

try:
	with youtubeModule.YoutubeDL(userOpts) as vidObj:
		vidObj.download([mediaURL])
	shutil.make_archive("SWDLTMultipleDL","zip","SWDLTMultipleDL")
	subprocess.run("rm -r -f SWDLTMultipleDL")
	
except:
	print("Unable to download, continuing...")
	time.sleep(1)
	
finally:
	subprocess.run("fStart")
	subprocess.run("exit")
