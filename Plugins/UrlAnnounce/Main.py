#!/usr/bin/env python

import re
import requests

import logging
logger = logging.getLogger("UrlAnnounce")

from .Settings import Settings

RE_TITLE = re.compile("<title>(.*?)</title>")

class Main(object):
	def __init__(self, Name, Parser):
		self.__name__ = Name
		self.Parser = Parser
		self.IRC = self.Parser.IRC
		try:
			self.ip = self.getIP()
		except (requests.HTTPError, requests.ConnectionError) as e:
			self.ip = None

	def getIP(self):
		return requests.get("http://icanhazip.com/").text.strip()

	def url(self, data):
		for x in " ".join(data[3:])[1:].split():
			match = re.match(Settings.get("url_regex"), x)
			if match:
				for bl in Settings.get("blacklist"):
					if re.search(bl, x):
						logger.info("Ran into blacklisted site, stopping here.")
						return None
				try:
					title = self.getTitle(x)
					if self.ip:
						if re.search(re.escape(self.ip), title):
							title = "127.0.0.1"
				except (requests.HTTPError, requests.ConnectionError) as e:
					logger.exception("Failed to connect")
					return None
				self.IRC.say(data[2], "Title: '{0}' (at {1})".format(title, match.group(2)))

	def getTitle(self, url):
		r = requests.get(url)
		r.raise_for_status()
		html = r.text
		title = RE_TITLE.search(html)
		if title:
			return title.group(1)
		logger.info("No title found for {0}".format(r.url))
		return Settings.get("no_title")



	def Load(self):
		self.Parser.hookCommand('PRIVMSG', self.__name__, {Settings.get("url_regex"): self.url})

	def Unload(self):
		pass
	def Reload(self):
		pass
