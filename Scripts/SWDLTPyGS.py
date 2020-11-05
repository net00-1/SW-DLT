import subprocess

print("Gathering URLs, please wait until you are redirected to Shortcuts. Process can take longer for bigger albums")

subprocess.run("gallery-dl -g mediaURL  > SWDLTTempURLs.txt")

subprocess.run("open shortcuts://run-shortcut?name=SW-DLT&input=text&text=%7B%22fName%22:%22gDownF%22%7D")
subprocess.run("exit")
