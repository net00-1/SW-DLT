import forkData (pyModule)
import subprocess

#SW-DLT Audio Download Script

#Get format for the audio, or video if audio is unavailable

userOpts = {"format":"genVars (defaultAD)","outtmpl":"SWDLTTempDL.%(ext)s","fixup":"never"}
mediaURL = 'mediaURL'

#Download audio, or video if audio is unavailable

with forkData (pyModule).YoutubeDL(userOpts) as vidObj:
	vidObj.download([mediaURL])
	
#Return to SWDLT with a specific function code
		
subprocess.run("open shortcuts://run-shortcut?name=SW-DLT&input=text&text=%7B%22fName%22:%22svaOutF%22,%22fType%22:%22Audio%22%7D")
subprocess.run("exit")
