#!/usr/bin/python2
#Taken from http://www.evaisse.net/2008/python-html-entities-decode-cgi-unescape-7002 
#because Python can't into having some decode function to do it.

import re
import htmlentitydefs

def convert(text):
	"""Decode HTML entities in the given text."""
	try:
		if type(text) is unicode:
			uchr = unichr
		else:
			uchr = lambda value: value > 255 and unichr(value) or chr(value)
		def entitydecode(match, uchr=uchr):
			entity = match.group(1)
			if entity.startswith('#x'):
				return uchr(int(entity[2:], 16))
			elif entity.startswith('#'):
				return uchr(int(entity[1:]))
			elif entity in htmlentitydefs.name2codepoint:
				return uchr(htmlentitydefs.name2codepoint[entity])
			else:
				return match.group(0)
		charrefpat = re.compile(r'&(#(\d+|x[\da-fA-F]+)|[\w.:-]+);?')
		text = charrefpat.sub(entitydecode, text)
		return text
	except:
		return text
