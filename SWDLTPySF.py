import subprocess
import time
import os
import re

#SW-DLT Self-Troubleshooter

print("Troubleshooting SW-DLT Installation.\n")
subprocess.run("cd")

#Checking for YouTube-dl, installing if not present, updating to latest available.

time.sleep(1)

if "WARNING: Package(s) not found: youtube-dl" in subprocess.getoutput("pip show youtube-dl"):
	print("YouTube-dl is missing, installing...\n")
	subprocess.run("pip -q install --upgrade youtube-dl")
	print("YouTube-dl has been installed.\n")
	
else:
	print("YouTube-dl present, updating...\n")
	subprocess.run("pip -q install --upgrade youtube-dl")
	print("Any available updates installed.\n")
	
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

#FFmpeg & Bin Folder Check, creating any missing component.

time.sleep(1)

if os.path.exists("./bin") == False:
	
	print("Bin folder & FFmpeg missing, installing...\n")
	
	subprocess.run("mkdir bin")
	subprocess.run("cd bin")
	subprocess.run("curl -L https://github.com/holzschu/a-Shell-commands/releases/download/0.1/ffmpeg.wasm -o ffmpeg.wasm")
	
	print("Bin folder & FFmpeg installed.\n")
	
else:
	
	subprocess.run("cd bin")
	
	if os.path.exists("./ffmpeg.wasm") == False:
		print("FFmpeg missing, installing...\n")
		
		subprocess.run("curl -L https://github.com/holzschu/a-Shell-commands/releases/download/0.1/ffmpeg.wasm -o ffmpeg.wasm")
		
		print("FFmpeg installed.\n")
		
	else:
		print("Bin folder and FFmpeg present.\n")

#Shortcuts home bookmark check, creating if not present

time.sleep(1)

bookMStatus = subprocess.getoutput("showmarks sHome")

if "not found" in bookMStatus:
	print("sHome bookmark missing, creating...\n")
	subprocess.run("cd $SHORTCUTS")
	subprocess.run("bookmark sHome")
	time.sleep(1)
	print("sHome bookmark created.\n")
	
else:
	print("sHome bookmark present.\n")

subprocess.run("cd")
time.sleep(1)

holdprocess = input("SW-DLT Troubleshooting process complete, enter any key to return to Shortcuts:\n")

subprocess.run("open shortcuts://")
