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

def upload_mkv(verbose=False):
	"""
	Call the script that uploads the MKV files
	"""
	if verbose:
		p.p_upload("MKV", True)
	os.system("src/mkv.sh")
	print()
	return

def upload_mp4(verbose=False):
	"""
	Call the script that uploads the MP4 files
	"""
	if verbose:
		p.p_upload("MP4", True)
	os.system("src/mp4.sh")
	print()
	return

def notify_mkv_encode(conf, mkv, izumi_type, verbose):
	"""
	Attempts to send encoding information to the encoding servers in order, until one accepts.
	If none accept, then the downloader itself will fallback (or cancel) by setting izumi_type
	"""

	# Create the request JSON
	body = dict()
	body['show'] = mkv['show_name']
	body['episode'] = mkv['new_filename']

	headers = dict()
	headers['Content-Type'] = "application/json"
	
	# Firstly, we attempt to do request a primary encoding. We need to mark it for failure
	# and fallback (if so), if so.
	PRIMARY_SUCCEED = False

	if verbose:
		p.p_notice("Now sending requests to encoding server(s)...", False)

	for encoder in conf['sync']['mkv']['encoders']['primary']:

		try:
			if verbose:
				p.p_request_encode_sending(encoder[0])

			try:
				# If there was a key before, we need to delete it...
				headers.pop("Authorization", None)
				headers['Authorization'] = encoder[1]
			except:
				pass

			r = requests.post(encoder[0], json=body, headers=headers, timeout=5)
			# Continue onto the next one, as the current failed
			if r.status_code != conf['sync']['mkv']['encoders']['status_code']:
				raise Exception("Bad status code!")

			# Else if succeeded, we mark it as passed and exit out
			if verbose:
				p.p_notify_sent(True)

			PRIMARY_SUCCEED = True
			break # Break out of the for loop and proceed to x265

		except:
			if verbose:
				p.p_notify_sent(False)

			continue
	print()

	if verbose:
		p.p_upload_notify("secondary server")

	# Now, we try to notify extra encoders.
	# However, if it fails, we don't do anything and just continue
	for encoder in conf['sync']['mkv']['encoders']['other']:
		try:
			if verbose:
				p.p_request_encode_sending(encoder[0])

			try:
				headers.pop("Authorization", None)
				headers['Authorization'] = encoder[1]
			except:
				pass

			r = requests.post(encoder[0], json=body, headers=headers, timeout=5)

			if r.status_code != conf['sync']['mkv']['encoders']['status_code']:
				# We just raise exception, since an error could be thrown while requesting
				raise Exception("Bad status code!")

			# Else if succeeded, just continue - we don't care
			if verbose:
				p.p_notify_sent(True)
			continue

		except:
			if verbose:
				p.p_notify_sent(False)
			continue

	print()

	# If all the encoders did not respond, then the downloader needs to fallback (if set so)
	# and encode (if so)
	if not PRIMARY_SUCCEED:
		if verbose:
			p.p_all_primary_enc_fail()

		# We only fallback if if specified to do so. Otherwise, just leave as is and return
		# to delete files.
		if conf['sync']['mkv']['encoders']['fallback']:
			if verbose:
				p.p_fallback_active()
			return "encoder"

	if verbose:
		p.p_primary_enc_success_or_no_fallback(izumi_type)

	return izumi_type