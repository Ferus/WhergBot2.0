#!/usr/bin/env python
import requests
import re
import json

class Imgur(object):
	"""Imgur API class.

	An instance of this class represents the json output from the Imgur API
	"""
	def __init__(self, picid):
		self.picid = picid
		self.url = 'http://imgur.com/gallery/{0}.json'
	def gallery(self):
		'''Returns Imgur gallery stats for given hash.'''
		r = requests.get(self.url.format(self.picid))
		try:
			r.raise_for_status()
		except (requests.HTTPError, requests.ConnectionError):
			return "Error connecting to API."
		try:
			r = json.loads(r.text)
		except ValueError:
			return None
		if r['status'] != 200 or r['success'] != True:
			return None
		return r['data']['image']

class Main(object):
	def __init__(self, Name, Parser):
		self.__name__ = Name
		self.Parser = Parser
		self.IRC = self.Parser.IRC

	def ImgurStats(self, data):
		hashes = re.findall('imgur\.com/(?:gallery/)?([\w\d]{5,7})', " ".join(data[3:]))
		hashes = list(set(hashes)) # Remove Duplicates.
		for picid in hashes[:3]: # Limit it to 3 per line.
			try:
				stats = Imgur(picid).gallery()
			except Exception as e:
				self.IRC.say(data[2], repr(e))
				return
			if isinstance(stats, dict):
				x = "\x02[Imgur]\x02 {0}".format(stats['title']) if stats.get('title') else ''
				x += " - [\x02{0}\x02 views]".format(stats['views']) if stats.get('views') else ''
				x += " - [\x02{0}\x02]".format(stats['gallery_timestamp']) if stats.get('gallery_timestamp') else ''
				x += " - [\x02{0}\x02 Points]".format(stats['points']) if stats.get('points') else ''
				x += " - [\x02{0}\x02 Likes]".format(stats['ups']) if stats.get('ups') else ''
				x += " - [\x02{0}\x02 Dislikes]".format(stats['downs']) if stats.get('downs') else ''
				self.IRC.say(data[2], x)
			else:
				# Keep errors quiet for now, this probably wasnt a gallery image but was caught by the regex
				pass

	def Load(self):
		self.Parser.hookCommand('PRIVMSG', self.__name__
		,{"(?:https?:\/\/)?(?:www\.)?(?:i\.)?imgur\.com\/(?:gallery\/)?[\w\d]{5,7}(?:\.)?(?:jpg|jpeg|png|gif)?": self.ImgurStats})

	def Unload(self):
		pass
	def Reload(self):
		pass
