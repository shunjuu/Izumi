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

def burn(inote):

	c = prints.Colors()
	p = prints.Printouts()
	verbose = conf['sys']['verbose']

	# Clear the terminal and print out the received argument
	os.system('clear') if os.name != "nt" else os.system('cls')
	p.p_initialize(inote, "convert") 

	# Load the config file, must be named "config.yml"
	conf = init.load_config()

	# Determine what type of Izumi we're running
	izumi_type = init.get_runtype(conf['type'])

	# Load a fixed inote string into an array
	# args = convert_inote_to_list(fix_args(inote, conf), conf)
	args = init.convert_inote_to_list(init.fix_args(inote, conf, verbose), conf, verbose)

	# -- GENERATE THE FILENAME STRINGS -- #
	p.p_notice("Now generating new filenames and filepaths...")

	# Create two dicts: One for MKV names and one for MP4 names
	mkv = dict()
	mp4 = dict()

	# Get the base name of the MKV file, and its MP4 equivalent
	filenames.get_source_filenames(mkv, mp4, args, verbose)

	# Get the show name, BE SURE TO RUN THIS BEFORE load_destination_folder_and_paths
	filenames.get_show_name(conf, mkv, mp4, args, verbose)

	# Use Anitopy to get the new, cleaned filenames
	filenames.generate_new_filenames(mkv, mp4, verbose)

	# Get the folders where a copy of the MKV and the new MP4 will be put.
	paths.load_destination_folder_and_paths(mkv, mp4, conf, args, verbose)
	paths.load_temp_folder_and_paths(mkv, mp4, conf, verbose)

	# Get ffmpeg executable information
	ffmpeg = dict()
	encode.load_ffmpeg_paths(ffmpeg, os.path.dirname(os.path.realpath(__file__)), verbose)
	
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
			p.p_double_shutil()
			sys.exit(2)

	# Step 2: Upload the file online, but only if mode is downloader
	# Step 2.5: If mode is downloader, only proceed from here if unsucessful call to proxies
	# Step 2.5: If mode is encoder, continue
	if izumi_type == "downloader":
		upload.upload_mkv(verbose)
		notify.notify_mkv_upload(conf, mkv, verbose)
		izumi_type = upload.notify_mkv_encode(conf, mkv, izumi_type, verbose)

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
		upload.upload_mp4(verbose)
		notify.notify_mp4_upload(conf, mp4, verbose)

		# Step 5.1: If we're originally just an encoder, we need to post one of the heavy servers
		# for file transferring, or fallback to just uploading everything
		# Check conf, not izumi_type, to see if original runtype is encoder or downloader
		if init.get_runtype(conf['type']) == "encoder":
			notify.distribute_mp4(conf)

	# step 6: Clear out all the new files
	cleanup.clear_files(conf, mkv, mp4, verbose)

	p.p_job_completed(mkv['src_filename'], True)
	sys.exit(0)

# Run convert if this file is invoked directly, which it will be
if __name__ == "__main__":
	burn(sys.argv[1])
