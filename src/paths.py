import sys, os
import shutil
import pprint as pp

import requests
import json, yaml

import anitopy

try:
	from src import prints
	from src import filenames
except:
	import prints
	import filenames

# Initialize our print statements and colors
c = prints.colors()
p = prints.printouts()


def load_destination_folder_and_paths(mkv, mp4, conf, args, verbose):
	"""
	Generates all the various folder paths that the system will neeed.
	Also loads the temp folder into MKV.

	Params:
		mkv: dict containing mkv property strings
		mp4: dict containing mp4 property strings
		conf: dict containing config.yml represented as dict
		args: the fixed version of inotify arg
		verbose: print verbose or not	
	"""

	# Safety check: Make sure the show names have been generated already
	if 'show_name' not in mkv or 'show_name' not in mp4:
		if verbose:
			p.p_warn_no_shownames()
			filenames.get_show_name(mkv, mp4, args, verbose)

	# First load the folders in for the MKV and make it append safe
	mkv['folder'] = os.path.abspath(conf['folders']['mkv'])
	# If path doesn't end with /, make it safe and add it.
	if not mkv['folder'].endswith('/'):
		mkv['folder'] += '/'

	# Generate the folder with the show name to place the new MKV file in
	mkv['new_hardsub_folder'] = mkv['folder'] + mkv['show_name'] + '/'
	# Generate the output MKV file string/path
	mkv['hardsubbed_file'] = mkv['new_hardsub_folder'] + mkv['new_filename']

	# Second, load the folders for the mp4 and make it append safe
	mp4['folder'] = os.path.abspath(conf['folders']['mp4'])
	# Append safe
	if not mp4['folder'].endswith('/'):
		mp4['folder'] += '/'

	# Genereate the folder with the show name to place the new MP4 file in
	mp4['new_hardsub_folder'] = mp4['folder'] + mp4['show_name'] + "/"
	# Generate the output MP$ file string/path
	mp4['hardsubbed_file'] = mp4['new_hardsub_folder'] + mp4['new_filename']

	if verbose:
		# MKV statemnts
		p.p_gen_path("MKV Base Folder", "mkv['folder']", mkv['folder'],
					False, False)
		p.p_gen_path("Hardsub Dest. Folder", "mkv['new_hardsub_folder']", 
					mkv['new_hardsub_folder'], True, False)
		p.p_gen_path("Hardsub Des. Filepath", "mkv['hardsubbed_file']",
					mkv['hardsubbed_file'], True, True)
		# MP4 statements
		p.p_gen_path("Hardsub Base Folder", "mp4['folder']", mp4['folder'],
					False, False)
		p.p_gen_path("Hardsub Destination Folder", "mp4['new_hardsub_folder']",
					mp4['new_hardsub_folder'], True, False)
		p.p_gen_path("Hardsub Destination Filepath", "mp4['hardsubbed_file']",
					mp4['hardsubbed_file'], True, True)

	return

def load_temp_folder_and_paths(mkv, mp4, conf, verbose):
	"""
	Helper method that generates the paths needed for the temp folder.
	While the MP4 dict is included for robustness, only MKV is modified.

	Exceptions: Throws an error if temp folder has a ' in the path.

	Params:
		Params:
		mkv: dict containing mkv property strings
		mp4: dict containing mp4 property strings
		conf: dict containing config.yml represented as dict
		args: the fixed version of inotify arg
		verbose: print verbose or not	
	"""

	# Load the temp folder and make it append safe
	mkv['temp'] = os.path.abspath(conf['folders']['temp'])
	if not mkv['temp'].endswith('/'):
		mkv['temp'] += '/'

	# Make sure the path is safe to read from, or raise an Exception.
	if "'" in mkv['temp']:
		p.p_fail_bad_temp_path()
		sys.exit(-5)

	# For safety, we need to literal quote every folder in the temp path,
	# or ffmpeg is going to throw a fit.
	temp_path = mkv['temp'].split("/")
	mkv['quoted_temp'] = str()
	for folder in temp_path:
		if folder:
			# Forcibly quote everything, shlex does not capture some delims
			mkv['quoted_temp'] = mkv['quoted_temp'] + "/" + "'" + folder + "'"
	mkv['quoted_temp'] += "/"

	# We'll also need a regular version of the path for shutil.copy2()
	# We use "temp.mkv" always as our temp name
	mkv['temp_file_path'] = mkv['temp'] + "temp.mkv"

	# Temporary file is guaranteed to be called "temp.mkv".
	# Get its path for -vf subtitles="path", quoted version
	mkv['quoted_temp_file_path'] = mkv['quoted_temp'] + "temp.mkv"

	if verbose:
		p.p_gen_path("MKV Temp. Folder", "mkv['temp']", mkv['temp'], 
					False, False)
		p.p_gen_path("MKV Quoted Temp. Folder", "mkv['quoted_temp']",
					mkv['quoted_temp'], True, True)
		p.p_gen_path("temp.mkv Regular File Path", "mkv['temp_file_path']",
					mkv['temp_file_path'], True, False)
		p.p_gen_path("Temp.mkv Subtitles Arg Path", 
					"mkv['quoted_temp_file_path']", mkv['quoted_temp_file_path'],
					True, True)
	return


