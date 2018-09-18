import sys, os
import re
import shutil
import pprint as pp

import requests # For making requests
import json, yaml # Parsing data

import anitopy # For generating renamed files

try: # Allow invocation as both a module and standalone
	from lib import hisha # For getting show names
	from src import prints # For pretty printing!
except:
	import hisha
	import prints

# Initialize our print statements and colors
c = prints.colors()

def get_source_filenames(mkv, mp4, args, verbose):
	"""
	This method takes the orignal filenames, and populates
	the MKV and MP4 dicts with the correct filenames.

	Params:
		mkv: dict containing mkv property strings
		mp4: dict containing mp4 property strings
		args: the fixed version of inotify arg
		verbose: Print verbose or not
	"""

	# The original filename is guaranteed to be args[2] from fixing
	mkv['src_filename'] = args[2]

	if verbose:
		p.p_gen_path("MKV Source Filename", "mkv['src_filename']", 
					 mkv['src_filename'], False, False)


	# Generate the full path of the source MKV file
	if not args[0].endswith('/'):
		args[0] += '/' # Add the / if it's missing
	mkv['src_file_path'] = args[0] + args[2]

	if verbose:
		p.p_gen_path("MKV Source Filepath", "mkv['src_file_path']",
					 mkv['src_file_path'], False, False)


	# Get the full path of the source MKV folder
	mkv['src_folder_path'] = args[0]
	if verbose:
		p.p_gen_path("MKV Source Folder Path", "mkv['src_folder_path']",
			mkv['src_folder_path'], False, True)

	return


if __name__ == "__main__":
	mkv = dict()
	mp4 = dict()
	args = ["/home/rocia/Videos/Incoming/Grand Blue", "CREATE", "Grand Blue - 01 [1080p].mkv"]
	get_source_filenames(mkv, mp4, args, True)