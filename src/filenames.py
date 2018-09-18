"""
filenames.py is a module to generate destination filenames of a
new file. This module does NOT generate paths.
"""

import sys, os
import re
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
p = prints.printouts()

def get_source_filenames(mkv, mp4, args, verbose):
	"""
	This method takes the orignal filenames, and populates
	the MKV and MP4 dicts with the correct filenames.

	Params:
		mkv: dict containing mkv property strings
		mp4: dict containing mp4 property strings
		args: the fixed version of inotify arg
		verbose: print verbose or not
	"""

	# The original filename is guaranteed to be args[2] from fixing
	mkv['src_filename'] = args[2]

	# Generate the full path of the source MKV file
	if not args[0].endswith('/'):
		args[0] += '/' # Add the / if it's missing
	mkv['src_file_path'] = args[0] + args[2]

	# Get the full path of the source MKV folder
	mkv['src_folder_path'] = args[0]

	if verbose:
		p.p_gen_path("MKV Source Filename", "mkv['src_filename']", 
					 mkv['src_filename'], False, False)
		p.p_gen_path("MKV Source Filepath", "mkv['src_file_path']",
					 mkv['src_file_path'], False, False)
		p.p_gen_path("MKV Source Folder Path", "mkv['src_folder_path']",
					 mkv['src_folder_path'], False, True)

	return


def clean_filename(filename, ext):
	"""
	Helper method.
	Returns a string that is the cleaned version of "filename".

	Requires anitopy to parse.

	Params:
		filename: The original video's filename
		ext: New extension to add to cleaned filename
				Should be in the form ".ext"
	"""
	a = anitopy.parse(filename)
	new_file = a['anime_title'] + " - " + a['episode_number']

	# If uncensored, we want to mark it
	if 'other' in a and 'uncensored' in a['other'].lower():
		new_file += " (Uncensored)"		

	# Add resolution if it's in the filename
	if 'video_resolution' in a:
		new_file = new_file + " [" + a['video_resolution'] + "]"

	new_file += ext
	return new_file


def generate_new_filenames(mkv, mp4, verbose):
	"""
	Populates MKV and MP4 dicts with new cleaned names.
	Requires anitopy as ad ependency

	Params:
		mkv: dict containing mkv property strings
		mp4: dict containing mp4 property strings
		verbose: print verbose or not
	"""

	# Use the clean filename to generate the new clean filename
	mkv['new_filename'] = clean_filename(mkv['src_filename'], ".mkv")
	mp4['new_filename'] = clean_filename(mkv['src_filename'], ".mp4")

	if verbose:
		p.p_gen_path("MKV New Filename", "mkv['new_filename']",
					 mkv['new_filename'], True, False)	
		p.p_gen_path("MP4 New Filename", "mp4['new_filename']",
					 mp4['new_filename'], True, True)


def get_show_name(conf, mkv, mp4, args, verbose):
	"""
	Gets the show name from the args path and loads it into two dictionaries.

	New in version 3.1: Show names could be predefined or are not included.
	Case 1: Use standard logic, get path by regex removing the show name
	Case 2: Use Hisha to determine the correct show_name

	Params:
		conf: Configuration file loaded from yml
		mkv: dict containing mkv property strings
		mp4: dict containing mp4 property strings
		args: the fixed version of inotify arg 
		verbose: print verbose or not
	"""
	parent_path = mkv['src_folder_path'] # Note: as args[0], this should always end in a '/'
	parent_path = parent_path if parent_path.endswith('/') else (parent_path + '/')
	parent_path = os.path.abspath(parent_path)

	# conf watch is just from config.yml, append / if necessary
	conf_watch_path = conf['folders']['watch']
	conf_watch_path = conf_watch_path if conf_watch_path.endswith('/') else (conf_watch_path + '/')
	conf_watch_path = os.path.abspath(conf_watch_path)

	# If the configuration watch folder path is the same as the parent path up to the file, this means
	# the file was placed in the root of watch, so we need to find the show name using Hisha.
	if parent_path == conf_watch_path:
		if verbose:
			p.p_hisha_usage(True)
		show_name = hisha.hisha(mkv['src_filename'])
	# Else, this means the show was placed in a folder with a predetermined name, so we use that instead
	else:
		if verbose:
			p.p_hisha_usage(False)
		show_abs_path = args[0]
		show = re.match('.*\/(.*)\/', show_abs_path)
		show_name = show.group(1)

	mkv['show_name'] = show_name
	mp4['show_name'] = show_name

	# Print out the data if requested
	if verbose:
		p.p_gen_path("Show Name", "mkv/mp4['show_name']", show_name, True, True)

	print()
	return
