import youtubeModule
import subprocess
import time

#SW-DLT Video Download Script

mediaURL = 'mediaURL'
userOpts = {"format":"","outtmpl":"SWDLTTempDL.%(ext)s","fixup":"detect_or_warn"}

try:
	with youtubeModule.YoutubeDL(userOpts) as vidObj:
		vidObj.download([mediaURL])
		
except:
	print("Unable to download, continuing...")
	time.sleep(1)

finally:
	subprocess.run("open shortcuts://run-shortcut?name=SW-DLT&input=text&text=%7B%22fName%22:%22svaOutF%22,%22fType%22:%22Video%22%7D")
	subprocess.run("exit")
