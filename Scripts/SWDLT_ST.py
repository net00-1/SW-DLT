import subprocess
import time
import os
import re

#SW-DLT Self-Troubleshooter

curTool = "forkData (utilName)"

print("Troubleshooting SW-DLT Installation.\n")
subprocess.run("cd")

#Checking for YouTube-dl/dlc, installing if not present, updating to latest available.

time.sleep(1)
if "WARNING: Package(s) not found: forkData (utilName)" in subprocess.getoutput("pip show forkData (utilName)"):
	
	print("forkData (disName) is missing, installing...\n")
	subprocess.run("pip -q install --upgrade forkData (utilName)")
	print("forkData (disName) has been installed.\n")
	
else:
	
	print("forkData (disName) present, updating...\n")
	subprocess.run("pip -q install --upgrade forkData (utilName)")
	print("Any available updates installed.\n")

#Detecting extra YouTube-dl/dlc and prompting for uninstall

time.sleep(1)
if curTool == "youtube-dlc":
	
	if "WARNING: Package(s) not found: youtube-dl" not in subprocess.getoutput("pip show youtube-dl"):
			
		delChoice = input("Warning: You are using YouTube-dlc. YouTube-dl is also installed. Would you like to remove it? (y/n)\n")
		if delChoice =="y":
			
			subprocess.run("pip uninstall -y youtube-dl")
			print("YouTube-dl removed.\n")
			
else:
	
	if "WARNING: Package(s) not found: youtube-dlc" not in subprocess.getoutput("pip show youtube-dlc"):
		
		delChoice = input("Warning: You are using YouTube-dl. YouTube-dlc is also installed. Would you like to remove it? (y/n)\n")		
		if delChoice =="y":
			
			subprocess.run("pip uninstall -y youtube-dlc")
			print("YouTube-dlc removed.\n")
	
#Checking for Gallery-dl, installing if not present, updating to latest available.

time.sleep(1)

if "WARNING: Package(s) not found: gallery-dl" in subprocess.getoutput("pip show gallery-dl"):
	print("Gallery-dl is missing, installing...\n")
	subprocess.run("pip -q install --upgrade gallery-dl")
	print("Gallery-dl has been installed.\n")
	
else:
	print("Gallery-dl present, updating...\n")
	subprocess.run("pip -q install --upgrade gallery-dl")
	print("Any available updates installed.\n")

#FFmpeg, FFprobe & Bin Folder Check, creating any missing component.

time.sleep(1)

if os.path.exists("./bin") == False:
	
	print("Bin folder, FFmpeg & FFprobe missing, installing...\n")
	
	subprocess.run("mkdir bin")
	subprocess.run("cd bin")
	subprocess.run("curl -L https://github.com/holzschu/a-Shell-commands/releases/download/0.1/ffmpeg.wasm -o ffmpeg.wasm")
	subprocess.run("curl -L https://github.com/holzschu/a-Shell-commands/releases/download/0.1/ffprobe.wasm -o ffprobe.wasm")
	
	print("Bin folder, FFmpeg & FFprobe installed.\n")
	
else:
	
	subprocess.run("cd bin")
	if os.path.exists("./ffmpeg.wasm") == False:
		
		print("FFmpeg missing, installing...\n")
		subprocess.run("curl -L https://github.com/holzschu/a-Shell-commands/releases/download/0.1/ffmpeg.wasm -o ffmpeg.wasm")
		print("FFmpeg installed.\n")
		
	elif os.path.exists("./ffprobe.wasm") == False:
		
		print("FFprobe missing, installing...\n")
		subprocess.run("curl -L https://github.com/holzschu/a-Shell-commands/releases/download/0.1/ffprobe.wasm -o ffprobe.wasm")
		print("FFprobe installed.\n")

	else:	
		print("Bin folder, FFmpeg & FFprobe present.\n")

#Shortcuts home bookmark check, creating if not present

time.sleep(1)
bookMStatus = subprocess.getoutput("showmarks sHome")

if "AppGroup" not in bookMStatus:
	
	print("sHome bookmark missing/incorrect, creating...\n")
	subprocess.run("cd $SHORTCUTS")
	subprocess.run("deletemark sHome")
	subprocess.run("bookmark sHome")
	print("sHome bookmark created.\n")
	
else:
	print("sHome bookmark present & correct.\n")

subprocess.run("cd")
time.sleep(1)

holdprocess = input("SW-DLT Troubleshooting process complete, enter any key to return to Shortcuts:\n")

subprocess.run("open shortcuts://")

subprocess.run("cd $SHORTCUTS")
subprocess.run("rm -f SWDLT*.*")
subprocess.run("rm -f -r SWDLTMultipleDL")
