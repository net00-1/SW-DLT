import forkData (pyModule)
import subprocess

#SW-DLT Video Download Script

#Get format for the video matching or closest to user requirements

userOpts = {"format":"downOpts","outtmpl":"SWDLTTempDL.%(ext)s","fixup":"detect_or_warn"}
mediaURL = 'mediaURL'

#Download video matching or closest to user requirements

with forkData (pyModule).YoutubeDL(userOpts) as vidObj:
	vidObj.download([mediaURL])

#Return to SWDLT with a specific function code

subprocess.run("open shortcuts://run-shortcut?name=SW-DLT&input=text&text=%7B%22fName%22:%22svaOutF%22,%22fType%22:%22Video%22%7D")
subprocess.run("exit")
