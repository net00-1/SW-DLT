import youtube_dl
import subprocess
import re

#SW-DLT Video Download Script

#Get format for the video matching or closest to user requirements

userOpts = {"format":"downOpts","outtmpl":"SWDLTTempDL.%(ext)s","fixup":"never"}
mediaURL = 'mediaURL'

with youtube_dl.YoutubeDL(userOpts) as vidObj:
	vidInfo = vidObj.extract_info(mediaURL, download=False)
	outExt = vidInfo.get("ext",None)
	outF = vidInfo.get("format",None)

#Download video matching or closest to user requirements

with youtube_dl.YoutubeDL(userOpts) as vidObj:
	vidObj.download([mediaURL])

#Invoke ffmpeg to fix up malformed MP4s, skip for other formats & skip for all merged videos

if "+" not in outF:
	
	#Filters out merged with ffmpeg already
	
	if "mp4" in outExt:
		#Filters out anything besides mp4
		
		print("PROCESSING MP4: Please wait until you are redirected back to Shortcuts.")
		
		subprocess.run("ffmpeg -i SWDLTTempDL." + outExt + " -c copy SWDLTFixedDL." + outExt)
		subprocess.run("rm -f SWDLTTempDL." + outExt)
		subprocess.run("mv SWDLTFixedDL." + outExt + " SWDLTTempDL." + outExt)
