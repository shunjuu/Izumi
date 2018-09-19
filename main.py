import sys, os, shutil
import pprint as pp
import re

from subprocess import call
from time import sleep
from shlex import quote

import requests
import json, yaml 

import anitopy 

# For finding show names intelligently
from lib import hisha

# Modules!
from src import cleanup
from src import encode
from src import filenames
from src import initialize as init
from src import notify
from src import paths
from src import prints
from src import upload

class colors:
	"""
	Shell based colors for colored printing!
	"""
	HEADER = '\033[95m'
	OKBLUE = '\033[94m'
	OKGREEN = '\033[92m'
	GREEN = '\033[32m'
	WARNING = '\033[93m'
	LCYAN = '\033[0;96m'
	ORANGE = '\033[0;33m'
	MAGENTA = '\033[35m'
	LMAGENTA = '\033[95m'
	FAIL = '\033[91m'
	ENDC = '\033[0m'
	BOLD = '\033[1m'
	UNDERLINE = '\033[4m'

def distribute_mp4(conf):
	"""
	Makes a blank POST request to various destinations to notify them to distribute new MP4s
	"""
	
	print(colors.LCYAN + "INFO: " + colors.ENDC +
			"Sending requests to distribute newly generate MP4 file(s)...")

	print(colors.WARNING + "NOTICE: " + colors.ENDC +
			"Now sending requests to "
			+ colors.WARNING + "ALWAYS" + colors.ENDC +
			" destinations...")
	# First, post all of the "always" destinations
	for distributor in conf['sync']['mp4-distribution']['distributors']['always']:
		print(colors.LCYAN + "NOTIFICATION: " + colors.ENDC +
				"Sending request to " + 
				colors.OKBLUE + distributor + colors.ENDC +
				"... ",end="")
		try:
			r = requests.post(distributor, timeout=5)
			print(colors.OKGREEN + "Success." + colors.ENDC)
		except:
			print(colors.FAIL + "Failed." + colors.ENDC)

	# Second, try the sequential ones until one passes or all fail
	print(colors.WARNING + "NOTICE: " + colors.ENDC +
			"Now sending requests to "
			+ colors.WARNING + "SEQUENTIAL" + colors.ENDC +
			" destinations...")
	for distributor in conf['sync']['mp4-distribution']['distributors']['sequential']:
		print(colors.LCYAN + "NOTIFICATION: " + colors.ENDC +
				"Sending request to " + 
				colors.OKBLUE + distributor + colors.ENDC +
				"... ",end="")
		try:
			r = requests.post(distributor, timeout=60)
			print(colors.OKGREEN + "Success" + colors.ENDC + ".")
			break
		except:
			print(colors.FAIL + "Failed" + colors.ENDC + ".")

	print()
	return


def burn(inote):

	c = prints.colors()
	p = prints.printouts()

	# Clear the terminal and print out the received argument
	os.system('clear') if os.name != "nt" else os.system('cls')
	p.p_initialize(inote, "convert") 

	# Load the config file, must be named "config.yml"
	conf = init.load_config()

	# Determine what type of Izumi we're running
	izumi_type = init.get_runtype(conf['type'])

	# Load a fixed inote string into an array
	# args = convert_inote_to_list(fix_args(inote, conf), conf)
	args = init.convert_inote_to_list(init.fix_args(inote, conf, False), conf, False)

	# -- GENERATE THE FILENAME STRINGS -- #
	p.p_notice("Now generating new filenames and filepaths...")

	# Create two dicts: One for MKV names and one for MP4 names
	mkv = dict()
	mp4 = dict()

	# Get the base name of the MKV file, and its MP4 equivalent
	filenames.get_source_filenames(mkv, mp4, args, False)

	# Get the show name, BE SURE TO RUN THIS BEFORE load_destination_folder_and_paths
	filenames.get_show_name(conf, mkv, mp4, args, False)

	# Use Anitopy to get the new, cleaned filenames
	filenames.generate_new_filenames(mkv, mp4, False)

	# Get the folders where a copy of the MKV and the new MP4 will be put.
	paths.load_destination_folder_and_paths(mkv, mp4, conf, args, False)
	paths.load_temp_folder_and_paths(mkv, mp4, conf, False)

	# Get ffmpeg executable information
	ffmpeg = dict()
	encode.load_ffmpeg_paths(ffmpeg, os.path.dirname(os.path.realpath(__file__)), False)
	
	# --------------------------------------------------------------------- #
	# String generation is complete, start to run transfer process
	# Note; izumi_type is the current type of downloader
	# --------------------------------------------------------------------- #
   
	# Step 1: We always want to copy the new file to a MKV: 
	# Note: Deprecation since we're using a temp file, we technically only want
	# to do this if we're in DOWNLOADER mode
	if izumi_type == "downloader":
		if not os.path.exists(mkv['new_hardsub_folder']):
			os.makedirs(mkv['new_hardsub_folder'])
		try:
			shutil.copy2(mkv['src_file_path'], mkv['hardsubbed_file'], follow_symlinks=True)
		except:
			print(colors.FAIL + "WARNING: " + colors.ENDC + 
					"Shutil was unable to copy into the temp file.")
			print(colors.WARNING + "NOTE: " + colors.ENDC +
					"This is probably just a duplicate autotools inotify notification.")
			sys.exit(2)

	# Step 2: Upload the file online, but only if mode is downloader
	# Step 2.5: If mode is downloader, only proceed from here if unsucessful call to proxies
	# Step 2.5: If mode is encoder, continue
	if izumi_type == "downloader":
		upload.upload_mkv(False)
		notify.notify_mkv_upload(conf, mkv, True)
		izumi_type = upload.notify_mkv_encode(conf, mkv, izumi_type, True)
		
	"""

	# Type check for encoder, as if encoder request succeeds, it will still continue 
	# to clear the files at the end
	if izumi_type == "encoder":
		# Step 3: Copy the file into a temp.mkv in temp for encoding
		shutil.copy2(mkv['src_file_path'], mkv['temp_file_path'], follow_symlinks=True)

		# Step 4: Execute ffmpeg script to encode videos
		# Make the directory the new folder will be in
		if not os.path.exists(mp4['new_hardsub_folder']):
			os.makedirs(mp4['new_hardsub_folder'])
		os.system("src/encode.sh %s %s"
				% (mkv['quoted_temp_file_path'], quote(mp4['hardsubbed_file'])))

		# Step 5: Upload the new MP4 file 
		upload.upload_mp4(False)
		notify.notify_mp4_upload(conf, mp4, False)

		# Step 5.1: If we're originally just an encoder, we need to post one of the heavy servers
		# for file transferring, or fallback to just uploading everything
		# Check conf, not izumi_type, to see if original runtype is encoder or downloader
		if get_runtype(conf['type']) == "encoder":
			distribute_mp4(conf)
	"""
	# step 6: Clear out all the new files
	cleanup.clear_files(conf, mkv, mp4, False)

	print(colors.OKGREEN + "Completed job for: " + colors.ENDC + 
			mkv['src_filename'] + ".")
	print()
	print()
	print()
	sys.exit(0)

# Run convert if this file is invoked directly, which it will be
if __name__ == "__main__":
	burn(sys.argv[1])
