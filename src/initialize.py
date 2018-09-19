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

def load_config():
	"""
	Loads our YAML or JSON file into a dict.
	Right now it's just YAML...
	"""

	with open("config.yml", 'r') as conf:
		try:
			return yaml.load(conf)
		except:
			p.p_bad_config("config.yml")
			sys.exit(2)

def get_runtype(input_type):
	"""
	Takes the input_type string and gets the runtype from it.
	Returns "downloader" or "encoder".

	Method is mostly just to make sure that any similar-enough string 
	in the "type" is loaded properly.
	"""

	lower_type = input_type.lower()
	rtype = str()
	if lower_type.startswith("d"):
		rtype = "downloader"
	elif lower_type.startswith("e"):
		rtype = "encoder"
	else:
		print()
		raise Exception("No proper config type found in config.yml!")
	
	p.p_runtype(rtype)
	return rtype


def convert_inote_to_list(inote, conf, verbose=False):
	"""
	This converts the inotifywait string returned in fix_args()
	to an array for the rest of the program to use.

	Note we need this method because if shows contain a "comma" in the name,
	str.split(',') will split on that too, in which case we need to reconnect
	the show names.

	Update v3: Delimiter has been changed to default ||. 
	All we need to do is split and return it.
	"""

	# Get the delimiter
	inote_delim = conf['sys']['delimiter']

	# Now split it up
	args = inote.split(inote_delim)

	if verbose:
		p.p_inote_details("convert_inote_to_list", "Using delimiter", inote_delim, False)
		p.p_inote_details("convert_inote_to_list", "Returning", str(args), True)

	return args


def fix_args(inote, conf):
	"""
	Function that will parse the inotifywatch strings sent to the machine.
	If new arg is a directory, it will "fix" the argument and return it.

	Params:
		inote: An inotifywait/wait style string
		runtype: Either "downloader" or "encoder"

	Observe there are two types of inputs:
	...folder/,CREATE,file.mkv ...path/,"CREATE,ISDIR",folder_name

	This method returns the first if given so, and alters the second to
	become the first. Note that the list of files array must be length 1.
	This is becase:
		1. If the folder already exists, the new dir will not be invoked
		2. Any other files should already have been deleted prior to invoke
	"""

	# Get the delimiter for the inote string passed in
	inote_delim = conf['sys']['delimiter']
	args = inote.split(inote_delim)

	# The most standard case: A new file is presented, devoid of folder
	if 'isdir' not in inote.lower():

		p.p_fix_args("fix_args", 
			"Detected a regular, non-directory file object was created.",
			False, None, False)
		"""
		print(colors.LCYAN + "INFO: " + colors.ENDC + 
				colors.OKBLUE + "<fix_args>" + colors.ENDC + " " + 
				"Detected a regular, non-directory file object was created.")
		"""

		# The name of the file that was JUST MADE.
		# (We assume the delimiter is always working properly.)
		new_filename = args[2]

		try:
			if new_filename.endswith(".meta"):
				print(colors.FAIL + "FAIL: " + colors.ENDC + 
						colors.OKBLUE + "<fix_args>" + colors.ENDC + " " +
						"The new file created was a meta file. Ignoring the file and exiting.")
				sys.exit(1)

		except SystemExit:
			print()
			sys.exit(1)

		"""
		print(colors.LCYAN + "INFO: " + colors.ENDC +
				colors.OKBLUE + "<fix_args>" + colors.ENDC + " " +
				"New file is not a meta file.")
		"""
		p.p_fix_args("fix_args", "New file is not a meta file.", False, None, False)
		
		print(colors.LCYAN + "INFO: " + colors.ENDC + 
				colors.OKBLUE + "<fix_args>" + colors.ENDC + " " + 
				"Returning unmodified inote: " + 
				"\"" + colors.WARNING + inote + colors.ENDC + "\"")

		print()
		return inote

	# A more common case, where the new directory is linked in.
	elif 'isdir' in inote.lower():
		print(colors.LCYAN + "INFO: " + colors.ENDC +
				colors.OKBLUE + "<fix_args>" + colors.ENDC + " " +
				"Detected a new directory was made.")

		# If we're running anything but a downloader, we need to ignore dirs.
		# Only the downloader needs to scan the dir (for ruTorrent)
		if conf['type'].lower() != "downloader":
			print(colors.FAIL + "FAIL: " + colors.ENDC +
					colors.OKBLUE + "<fix_args>" + colors.ENDC + " " +
					"The runtype is not Downloader. Exiting the system...")
			print()
			sys.exit(0)

		else:
			print(colors.LCYAN + "INFO: " + colors.ENDC + 
					colors.OKBLUE + "<fix_args>" + colors.ENDC + " " + 
					"The runtype is Downloader. Proceeding to scan the directory for file(s).")
		
		# args[0] is the path up to the folder, args[3] is the name of the folder itself
		# folder name is args[3], not args[2], because extra comma is inserted between
		# CREATE,ISDIR, increasing the array length by 1
		# Update: args[2] instead of args[3] due to changes in delimiting to ||
		path = args[0] + args[2] + "/"
		print(colors.LCYAN + "INFO: " + colors.ENDC + 
				colors.OKBLUE + "<fix_args>" + colors.ENDC + " " + 
				"Scanning: " + 
				colors.WARNING + "\"" + path + "\"" + colors.ENDC)

		# Get all the files in the new dir, there should only be a single .mkv softlink
		files = os.listdir(path)
		files = [f for f in files if f.endswith(".mkv")]

		# Make sure we only have one file
		if len(files) != 1:
			print(colors.FAIL + "FAIL: " + colors.ENDC +
					colors.OKBLUE + "<fix_args>" + colors.ENDC + " " +
					"Detected " + str(len(files)) + " files in the directory. Exiting..")
			print()
			sys.exit(1)

		new_inote = path + inote_delim + "CREATE" + inote_delim + files[0]
		print(colors.LCYAN + "INFO: " + colors.ENDC + 
				colors.OKBLUE +"<fix_args>" + colors.ENDC + " " + 
				"Returning new inote: " + 
				colors.WARNING + new_inote + colors.ENDC)

		print()
		return new_inote