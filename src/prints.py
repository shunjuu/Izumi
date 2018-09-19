"""
colors.py contains a single class that defines print colors
that can be used in print statements for Unix.
"""

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


class printouts:
	"""
	Statements to be printed out to the terminal.
	Use these functions to make less repetitive.
	"""
	def __init__(self):	
		self.c = colors()

	def p_initialize(self, inote, func_name, endgroup=True):
		"""
		Print the initial print statement
		"""
		print("%sINFO: %s<%s>%s Received Argument: \"%s%s%s\"" % (
			self.c.LCYAN, self.c.OKBLUE, func_name, self.c.ENDC,
			self.c.WARNING, inote, self.c.ENDC))
		if endgroup:
			print()

	def p_bad_config(self, conf_name):
		"""
		Print statement for bad config files...
		"""
		print("%sFAIL:%s An exception has occured while loading: %s" % (
			self.c.FAIL, self.c.ENDC, conf_name))


	def p_fix_args(self, func_name, details, quote_details, 
					additional_details, endgroup=False):
		"""
		Params:
			func_name: Name of the invoking function (str)
			details: (Something): (str)
			quote_details: Whether or not to encapsulate details in " (bool)
			additional_details: if quote_details, what quote? (str)
			endgroup: extra print (bool)
		"""
		if not quote_details:
			print("%sINFO: %s<%s>%s %s" % (
				self.c.LCYAN, self.c.OKBLUE, func_name, self.c.ENDC,
				details))

		elif quote_details:
			print("%sINFO: %s<%s>%s %s: %s\"%s\"%s" % (
				self.c.LCYAN, self.c.OKBLUE, func_name, self.c.ENDC,
				details, self.c.WARNING, str(additional_details),
				self.c.ENDC))

		if endgroup:
			print()

	def p_fix_args_fail(self, func_name, details, endgroup=True):
		print("%sFAIL: %s<%s>%s %s" % (
			self.c.FAIL, self.c.OKBLUE, func_name, self.c.ENDC,
			details))

		if endgroup:
			print()

	def p_runtype(self, mode, endgroup=True):
		print("%sNOTICE:%s Using mode \"%s%s%s\"." % (
			self.c.GREEN, self.c.ENDC, self.c.OKGREEN, mode, self.c.ENDC))
		if endgroup:
			print()

	def p_inote_details(self, func_name, note, note_details, endgroup=True):
		print("%sINFO:%s <%s>%s %s: %s%s%s" % (
			self.c.LCYAN, self.c.OKBLUE, func_name, self.c.ENDC,
			note, self.c.WARNING, note_details, self.c.ENDC))

		if endgroup:
			print()


	def p_gen_path(self, name, sys_name, sys_value, light=False, endgroup=False):
		"""
		At the beginning of Izumi, all the paths are generated. This method removes
		us having to write each print statement, instead just calling this method. 

		Actions: Prints to stdout

		Params:
			self: class identifier
			name: User-identifiable name for the following print
			sys_name: The string of variable used by the system for the referenced value
			sys_value: The actual variable itself (sys_value is just the string of the variable name)
			light: If we want to print in light magenta (default: dark magenta)
			endgroup: Signifies this is the end of a group print, and we need to print a newline after
		"""

		# Change magenta appropriately
		if light:
			MAGENTA = self.c.LMAGENTA
		else:
			MAGENTA = self.c.MAGENTA

		# Print the information out there, using string formatting to simplify it
		print("%sINFO:%s %s:%s < %s >%s %s %s" %
			(self.c.FAIL, self.c.ENDC, name, self.c.OKBLUE, 
			sys_name, MAGENTA, sys_value, self.c.ENDC,))

		# If this is the end of a group, we print an extra newline
		if endgroup:
			print()

		return

	def p_hisha_usage(self, used):
		"""
		Print statements for if Hisha was used or not
		"""
		if used:
			print("%sNOTICE:%s %s %s" % (
				self.c.GREEN, self.c.ENDC,
				"A show name was not specified in the path of the new episode.",
				"Using Hisha to determine the show name.",))
		else:
			print("%sNOTICE:%s %s %s" % (
				self.c.GREEN, self.c.ENDC,
				"A show name was specified in the path of the new episode.",
				"Not using Hisha",))

	def p_warn_no_shownames(self):
		print("%sNOTICE:%s get_show_name()%s not yet invoked. Invoking..." % (
				self.c.WARNING, self.c.FAIL, self.c.ENDC,))

	def p_fail_bad_temp_path(self):
		print("%sFAIL:%s %s %s" % (
			self.c.FAIL, self.c.ENDC,
			"Unexpected single quote was found in the temp folder path.",
			"The program will now exit."))

	def p_notice(self, note, endgroup=True):
		"""
		General notice staetment printout
		"""
		print("%sNOTICE: %s%s" % (self.c.GREEN, self.c.ENDC, note))

		if endgroup:
			print()

	def p_clear_notice(self, name):
		"""
		Prints out the notice statemnet for file deletion
		"""
		print("%sNOTICE:%s Now deleting: %s%s%s files." % (
			self.c.WARNING, self.c.ENDC, self.c.WARNING, name, self.c.ENDC))

	def p_clear_before(self, name, sys_name):
		"""
		Print statement for before something is attempted to be deleted.
		"""
		print("%sDELETING:%s %s: %s%s%s..." % (
			self.c.FAIL, self.c.ENDC, name, self.c.WARNING, 
			sys_name, self.c.ENDC), end="")

	def p_clear_after(self, success, endgroup=False):
		"""
		Print statement for deletion attempt status.
		"""
		if success:
			print("%sSuccess%s." % (self.c.OKGREEN, self.c.ENDC))
		else:
			print("%sFailed%s." % (self.c.FAIL, self.c.ENDC))

		# If this is the end, we want to print an extra space afterwards.
		if endgroup:
			print()

	def p_clear_after_hisha(self):
		"""
		Specifically for deleting source folder with hisha
		"""
		print("%sIgnored, used Hisha%s." % (self.c.OKGREEN, self.c.ENDC))
		print()

	def p_upload(self, upload_type, endgroup=True):
		"""
		Print statement to shell for notifying a MKV file
		"""
		print("%sINFO:%s Now uploading %s files..." % (
			self.c.LCYAN, self.c.ENDC, upload_type))

		if endgroup:
			print()

	def p_upload_notify(self, upload_type):
		"""
		Print statement for sending upload notifications (to Aleytia)
		"""
		print("%sINFO:%s Now sending %s upload notifications..." % (
			self.c.LCYAN, self.c.ENDC, upload_type))

	def p_upload_notify_sending(self, url):
		"""
		"Sending notification to ..."
		"""
		print("%sNOTIFICATION:%s Sending notification to %s%s%s... " % (
			self.c.LCYAN, self.c.ENDC, self.c.OKBLUE, url, self.c.ENDC),
			end="")

	def p_notify_sent(self, success, endgroup=False):
		"""
		Print statement for deletion attempt status.
		"""
		if success:
			print("%sSuccess%s." % (self.c.OKGREEN, self.c.ENDC))
		else:
			print("%sFailed%s." % (self.c.FAIL, self.c.ENDC))

		# If this is the end, we want to print an extra space afterwards.
		if endgroup:
			print()

	def p_request_encode_sending(self, encoder):
		"""
		Print statement when attempting to send an encode request
		"""
		print("%sNOTIFICATION: %sSending encode request to %s%s%s... " % (
			self.c.LCYAN, self.c.ENDC, self.c.OKBLUE, encoder, self.c.ENDC),
			end="")

	def p_all_primary_enc_fail(self):
		print("%sINFO:%s None of the primary encoders were successful." % (
			self.c.WARNING, self.c.ENDC))

	def p_fallback_active(self, endgroup=True):
		print("%sWARNING: %sFallback mode is activated. Now switching to %sencoder%smode." % (
			self.c.WARNING, self.c.ENDC, self.c.WARNING, self.c.ENDC))
		if endgroup:
			print()

	def p_primary_enc_success_or_no_fallback(self, izumi_type, endgroup=True):
		print("%sNOTICE:%s %s %s %s %s %s mode." % (
			self.c.WARNING, self.c.ENDC,
			"A primary encoder request was successful or fallback is deactivated.",
			"Continuing as", self.c.WARNING, izumi_type, self.c.ENDC))
		
		if endgroup:
			print()

	def p_start_distribute(self, endgroup=False):
		print("%sINFO:%s Sending requests to distribute newly generated MP$ file(s)..." %
			(self.c.LCYAN, self.c.ENDC))

		if endgroup:
			print()

	def p_distribute_notice(self, note_type, endgroup=False):
		"""
		Prints "NOTICE: Now sending request to <SEQUENTIAL/ALWAYS>...""
		"""
		print("%sNOTICE: %sNow sending requests to %s%s%s destinations..." % (
			self.c.WARNING, self.c.ENDC, self.c.WARNING, note_type, self.c.ENDC))

		if endgroup:
			print()

	def p_distribute_sending_request(self, distributor, endgroup=False)
		"""	
		Sends a post request to distribution servers for MP4 distribution.
		"""
		print("%sNOTIFICATION: %sSending request to %s%s%s... " % (
			self.c.LCYAN, self.c.ENDC, self.c.OKBLUE, distributor, self.c.ENDC),
			end="")

	def p_distribute_notice_sent(self, success, endgroup=False):
		"""
		Print statement for deletion attempt status.
		"""
		if success:
			print("%sSuccess%s." % (self.c.OKGREEN, self.c.ENDC))
		else:
			print("%sFailed%s." % (self.c.FAIL, self.c.ENDC))

		# If this is the end, we want to print an extra space afterwards.
		if endgroup:
			print()

	def p_double_shutil(self):
		print("%sWARNING:%s%s\n%sNOTE:%s %s." % (
			self.c.FAIL, self.c.ENDC,
			"Shutil was unable to copy into the temp file.",
			self.c.WARNING, self.c.ENDC,
			"This is likely a duplicate notification triggered by inotify."))

	def p_job_completed(self, filename, endgroup=True):
		"""
		The final print statement to clear it all up.
		"""
		print("%sCompleted job for: %s%s." % (
			self.c.OKGREEN, filename, self.c.ENDC))

		if endgroup:
			print(end="\n\n\n")

