"""
Similar to prints.py, but this is instead for server printouts 
to keep things relatively organized
"""
class Colors:
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

class Printouts:
	"""
	Statements to be printed out to the terminal.
	Use these functions to make less repetitive.
	"""

	def __init__(self):
		self.c = Colors()

	def p_encode_start(self, episode, start=True):

		if start:
			print()

		print("%sINFO:%s Received an encoding request for: %s%s%s." % (
			self.c.LCYAN, self.c.ENDC, self.c.WARNING,
			episode, self.c.ENDC))

	def p_encode_watch_detect(self, folder, endgroup=False):
		print("%sINFO: %sDetected watch folder at: %s%s%s." % (
			self.c.LCYAN, self.c.ENDC, self.c.WARNING,
			folder, self.c.ENDC))		

		if endgroup:
			print()

	def p_encode_show_folder_create(self, folder, endgroup=True):
		print("%sINFO:%s Created show folder at %s%s%s." % (
			self.c.LCYAN, self.c.ENDC, self.c.WARNING, 
			folder, self.c.ENDC))

		if endgroup:
			print()

	def p_encode_rclone_source(self, folder, endgroup=False):
		print("%sNOTICE:%s Sourcing from: \"%s%s%s\"." % (
			self.c.WARNING, self.c.ENDC, self.c.WARNING,
			folder, self.c.ENDC))

		if endgroup:
			print()

	def p_encode_rclone_saving_dest(self, folder, endgroup=True):
		print("%sNOTICE:%s Saving to: \"%s%s%s\"." % (
			self.c.WARNING, self.c.ENDC, self.c.WARNING,
			folder, self.c.ENDC))

		if endgroup:
			print()

	def p_encode_download_new_ep(self, endgroup=False):
		print("%sNOTICE:%s Downloading new episode..." % (
			self.c.WARNING, self.c.ENDC))

		if endgroup:
			print()

	def p_encode_completed(self, episode, endgroup=True):
		print("%sCompleted job for: %s%s" % (
			self.c.OKGREEN, self.c.ENDC, episode))

		if endgroup:
			print("\n\n")
