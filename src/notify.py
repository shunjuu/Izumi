import os, sys
import requests

import json

from lib import hisha

try:
	from src import prints
except:
	import prints

c = prints.colors()
p = prints.printouts()

def notify_mkv_upload(conf, mkv, verbose=False):
	"""
	Sends a POST request that will issue notifications about the new MKV.
	We use requests as shell curling is unreliable (and we want ot make this
	cross-operable as possible).
	"""

	p.p_upload_notify("MKV")	

	# Create the body
	body = dict()
	body['json-type'] = 1
	body['source'] = "Undefined" # Replace this with sys_name
	body['show_name'] = mkv['show_name']
	body['location'] = conf['notifications']['upload']['mkv']['name']
	body['file'] = mkv['new_filename']
	body['file_size'] = os.path.getsize(mkv['hardsubbed_file'])

	# Add a header unit for content-type and authorization
	headers = dict()
	headers['Content-Type'] = "application/json"

	for g in conf['notifications']['upload']['mkv']['urls']:
		if verbose:
			p.p_upload_notify_sending(g[0])

		# Add the header into the request, but only if it exists
		try:
			headers['Authorization'] = g[1] # g[1] is the key, if it exists
		except:
			pass

		try:
			r = requests.post(g[0], json=body, headers=headers, timeout=5)
			if verbose:
				p.p_notify_sent(True)
		except:
			if verbose:
				p.p_notify_sent(False)

	print()
	return


def notify_mp4_upload(conf, mp4, verbose=False):
	"""
	Sends a POST request that will issue notifications about the new MP4.
	We use requests as shell curling is unreliable (and we want ot make this
	cross-operable as possible).
	"""

	p.p_upload_notify("MP4")	

	# Create the body
	body = dict()
	body['json-type'] = 2
	body['source'] = "Undefined" # Replace this with sys_name
	body['show_name'] = mp4['show_name']
	body['location'] = conf['notifications']['upload']['mp4']['name']
	body['file'] = mp4['new_filename']
	body['file_size'] = os.path.getsize(mp4['hardsubbed_file'])

	# Add a header unit for content-type and authorization
	headers = dict()
	headers['Content-Type'] = "application/json"

	for g in conf['notifications']['upload']['mp4']['urls']:
		if verbose:
			p.p_upload_notify_sending(g[0])

		# Add the header into the request, but only if it exists
		try:
			headers['Authorization'] = g[1] # g[1] is the key, if it exists
		except:
			pass

		try:
			r = requests.post(g[0], json=body, headers=headers, timeout=5)
			if verbose:
				p.p_notify_sent(True)
		except:
			if verbose:
				p.p_notify_sent(False)

	print()
	return