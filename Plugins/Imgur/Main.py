#!/usr/bin/env python
import requests
import json

from .Settings import Settings

class Imgur(object):
	"""Imgur API class.

	An instance of this class represents the json output from the Imgur API
	"""
	def __init__(self, hash):
		self.hash = hash
		self.url = 'http://imgur.com/gallery/{0}.json'
	def gallery(self):
		'''Returns Imgur gallery stats for given hash.'''
		r = requests.get(self.url.format(self.hash))
		try:
			r.raise_for_status()
		except (requests.HTTPError, requests.ConnectionError):
			return "Error connecting to API."
		r = json.loads(r.text)['gallery']['image']
		return r

class Main(object):
	def __init__(self, Name, Parser):
		self.__name__ = Name
		self.Parser = Parser
		self.IRC = self.Parser.IRC

	def ImgurStats(self, data):
		hashs = re.findall('imgur\.com/(?:gallery/)?(\w{5})', " ".join(data[3:]))
		hashs = list(set(hashs)) # Remove Duplicates.
		for hash in hashs[:3]: # Limit it to 3 per line.
			try:
				stats = Imgur(hash).gallery()
			except Exception as e:
				self.IRC.say(data[2], repr(e))
				return
			x = "\x02[Imgur]\x02 {0}".format(stats['title'])
			x += " - [\x02{0}\x02 views]".format(stats['views'])
			x += " - [\x02{0}\x02]".format(stats['gallery_timestamp'])
			#Tail end.
			x += " - [\x02{0}\x02 Points]".format(stats['points'])
			x += " - [\x02{0}\x02 Likes]".format(stats['ups'])
			x += " - [\x02{0}\x02 Dislikes]".format(stats['downs'])
			self.IRC.say(data[2], x)

	def Load(self):
		self.Parser.hookCommand('PRIVMSG', "(?:https?:\/\/)?(?:www\.)?(?:i\.)?imgur\.com\/(?:gallery\/)?[a-zA-Z0-9]{5}(?:\.)?(?:jpg|jpeg|png|gif)?", self.ImgurStats)
		self.Parser.hookPlugin(self.__name__, Settings, self.Load, self.Unload, self.Reload)

	def Unload(self):
		pass
	def Reload(self):
		pass
