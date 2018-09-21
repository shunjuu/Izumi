import sys, os
import shutil
import pprint as pp 

import requests
import json, yaml

import anitopy

try:
	from src import prints
except:
	import prints

# Initialize our print statements and colors
c = prints.Colors()
p = prints.Printouts()

def load_ffmpeg_paths(ffmpeg, home, verbose=False):
	"""
	Helper method to load our appropriate ffmpeg paths into the system

	Params:
		ffmpeg: dict containing ffmpeg arguments
		home: passed from main, gives path of the main.py path
	"""
	# We want to get the current working directory for reference
	# WORK_DIR/bin/ffmpeg{-10bit,}
	# Design note: The ffmpeg conversion script should not have to
	# figure out where it is - pass in the full path of the executable
	ffmpeg['dir_path'] = home + "/bin/"
	ffmpeg['ffmpeg'] = ffmpeg['dir_path'] + "ffmpeg"
	ffmpeg['ffmpeg-10bit'] = ffmpeg['dir_path'] + "ffmpeg-10bit"

	if verbose:
		p.p_gen_path("Application \"bin\" directory", "ffmpeg['dir_path']", 
					ffmpeg['dir_path'], True, False)
		p.p_gen_path("ffmpeg executable path", "ffmpeg['ffmpeg']", ffmpeg['ffmpeg'],
					False, False)
		p.p_gen_path("ffmpeg-10bit executable path", "ffmpeg['ffmpeg-10bit']",
					ffmpeg['ffmpeg-10bit'], False, True)
	return
