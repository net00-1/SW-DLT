import youtubeModule
import subprocess
import time

#SW-DLT Audio Download Python Script

mediaURL = 'mediaURL'
userOpts = {"format":"","outtmpl":"SWDLTTempDL.%(ext)s","fixup":"never"}

try:
	with youtubeModule.YoutubeDL(userOpts) as vidObj:
		vidObj.download([mediaURL])	
	
except:
	print("Unable to download, continuing...")
	time.sleep(1)
	
finally:	
	subprocess.run("open shortcuts://run-shortcut?name=SW-DLT&input=text&text=%7B%22fName%22:%22svaOutF%22,%22fType%22:%22Audio%22%7D")
	subprocess.run("exit")
