import subprocess

print("Gathering URLs... Process will take longer for bigger albums.")

mediaURL = 'mediaURL'

subprocess.run("gallery-dl -g " + mediaURL + "GDLItems > SWDLTTempURLs.txt")

subprocess.run("open shortcuts://run-shortcut?name=SW-DLT&input=text&text=%7B%22fName%22:%22gDownF%22%7D")
subprocess.run("exit")
