import subprocess
import time

#SW-DLT Gallery-dl Download Script

print("Gathering URLs... Process will take longer for bigger albums.")
mediaURL = 'mediaURL'

try:
	subprocess.run("gallery-dl -g " + mediaURL + "GDLItems > SWDLTTempURLs.txt")
	
except:
	print("Unable to download, continuing...")
	time.sleep(1)

finally:
	subprocess.run("open shortcuts://run-shortcut?name=SW-DLT&input=text&text=%7B%22fName%22:%22gDownF%22%7D")
	subprocess.run("exit")
