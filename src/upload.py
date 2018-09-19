import os, sys
import requests

import json

from lib import hisha

try:
	from src import prints
except:
	import prints

c = prints.colors()
p = prints.printouts()

def upload_mkv():
	"""
	Call the script that uploads the MKV files
	"""
	p.p_upload("MKV", True)
	os.system("src/mkv.sh")
	print()
	return

def upload_mp4():
	"""
	Call the script that uploads the MP4 files
	"""
	p.p_upload("MP4", True)
	os.system("src/mp4.sh")
	print()
	return

