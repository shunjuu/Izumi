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

	def p_gen_path(self, name, sys_name, sys_value, light, endgroup):
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

if __name__ == "__main__":
	p = printouts()
	p.p_gen_path("mkv source filename", "mkv[src_filename']", "value", True, False)
	p.p_gen_path("mkv source filename", "mkv[src_filename']", "value", False, True)
