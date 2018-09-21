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

c = prints.Colors()
p = prints.Printouts()

	
def rmfile(name, path, verbose, endgroup=False):
	"""
	Helper method to try and delete a specific file.

	Params:
		name: User readable name of the path to be deleted, for printing
		path: The path of the file to be deleted
	"""
	if verbose:
		p.p_clear_before(name, path)

	try:
		os.remove(path)
		if verbose:
			p.p_clear_after(True, endgroup)
	except:
		if verbose:
			p.p_clear_after(False, endgroup)


def rmfolder(name, path, verbose, endgroup=False):
	"""
	Helper method to try and delete a specific folder

	Params:
		name: User readable name of the path to be deleted, for printing
		path: The path of the file to be deleted
	"""
	if verbose:
		p.p_clear_before(name, path)
	try:
		os.rmdir(path)
		if verbose:
			p.p_clear_after(True, endgroup)
	except:
		if verbose:
			p.p_clear_after(False, endgroup)

def rm_src_folder(name, conf, mkv, path, verbose, endgroup=True):
	"""
	Helper method to delete the source folder (if necessary)
	"""
	if verbose:
		p.p_clear_before(name, path)
	try:
		watch_folder = conf['folders']['watch']
		watch_folder = watch_folder if watch_folder.endswith('/') else (watch_folder + '/')

		mkv_src_fdr_path = mkv['src_folder_path']
		mkv_src_fdr_path = mkv_src_fdr_path if mkv_src_fdr_path.endswith("/") else (mkv_src_fdr_path + '/')	

		if watch_folder == mkv_src_fdr_path:
			# you MUST nest this if statement
			if verbose:
				p.p_clear_after_hisha()
		else:
			os.rmdir(path)
			if verbose:
				p.p_clear_after(True, endgroup)
	except Exception as e:
		if verbose:
			p.p_clear_after(False, endgroup)

	# Special single print if not verbose
	if not verbose:
		print()


def clear_files(conf, mkv, mp4, verbose):
	"""
	Deletes all the files once the system is done running.

	File deletions for each category are not similar, so we will
	code each one individually.

	This method prints differently: It must print in real time.

	Params:
		conf: Configuration file loaded from yml
		mkv: dict containing mkv property strings
		mp4: dict containing mp4 property strings
		verbose: print verbose or not
	"""

	# Start off by clearing the MKV files
	p.p_clear_notice("mkv")	
	rmfile("MKV Corrected File", mkv['hardsubbed_file'], verbose)
	rmfolder("MKV Corrected Folder", mkv['new_hardsub_folder'], verbose)

	p.p_clear_notice("mp4")
	rmfile("MP4 Hardsub File", mp4['hardsubbed_file'], verbose)
	rmfolder("MP4 Hardsub Folder", mp4['new_hardsub_folder'], verbose)

	p.p_clear_notice("temp")
	rmfile("Temp File", mkv['temp_file_path'], verbose)

	p.p_clear_notice("source")
	rmfile("Source File", mkv['src_file_path'], verbose)
	rm_src_folder("Source Folder", conf, mkv, mkv['src_folder_path'], verbose)
