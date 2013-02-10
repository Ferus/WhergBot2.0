#!/usr/bin/env python

import requests
import re
import json
from html import entities as htmlentitydefs
import logging
logger = logging.getLogger("UrbanDictionary")

from Parser import Locker
Locker = Locker(5)

from .Settings import Settings

def convert(text):
	"""Decode HTML entities in the given text."""
	try:
		if type(text) is str:
			uchr = chr
		else:
			uchr = lambda value: value > 255 and chr(value) or chr(value)
		def entitydecode(match, uchr=uchr):
			entity = match.group(1)
			if entity.startswith('#x'):
				return uchr(int(entity[2:], 16))
			elif entity.startswith('#'):
				return chr(int(entity[1:]))
			elif entity in htmlentitydefs.name2codepoint:
				return chr(htmlentitydefs.name2codepoint[entity])
			else:
				return match.group(0)
		charrefpat = re.compile(r'&(#(\d+|x[\da-fA-F]+)|[\w.:-]+);?')
		text = charrefpat.sub(entitydecode, text)
		return text
	except Exception as e:
		logger.exception("Error'd on convert()")
		return text

# http://www.urbandictionary.com/tooltip.php?term= <-- Thank god for this url.
# http://api.urbandictionary.com/v0/define?term= <-- Even better,
class Main(object):
	def __init__(self, Name, Parser):
		self.__name__ = Name
		self.Parser = Parser
		self.IRC = self.Parser.IRC

		self.CacheFile = Settings.get("CacheFile", "Plugins/UrbanDictionary/Cache.txt")

		# create it if it doesnt exist.
		try:
			c = open(self.CacheFile, 'r')
		except IOError:
			c = open(self.CacheFile, 'w')
		c.close()
		del c


	def checkCacheForDef(self, word):
		with open(self.CacheFile, 'r') as c:
			cache = c.read().split('\n')
			for line in cache:
				if line.startswith(word.lower()):
					return line.split(" : ")[1]
			else:
				return False

	def addWordToCache(self, word, definition=''):
		with open(self.CacheFile, 'a') as c:
			logger.info('Adding word {0}'.format(word))
			c.write("{0} : {1}\n".format(word, definition))

	def Main(self, data):
		if Locker.Locked:
			self.IRC.notice(data[0].split("!")[0], "Please wait a little bit longer before using this command.")
			return None
		word = ' '.join(data[4:])
		checkCache = self.checkCacheForDef(word)
		if checkCache:
			logger.info("Sending cached word.")
			self.IRC.say(data[2], "\x02[UrbanDict]\x02 {0}: {1}".format(word, checkCache))
			Locker.Lock()
			return None

		logger.info("Polling UrbanDictionary.")
		url = "http://www.urbandictionary.com/tooltip.php?term={0}".format(word.replace(" ","%20"))
		try:
			html = requests.get(url).text
		except requests.HTTPError:
			logger.exception("Failed to connect.")
			self.IRC.say(data[2], "Failed to connect to Urban Dictionary.")
			return None

		html = html.replace("\\u003C", "<").replace("\\u003E",">")
		html = json.loads(html)['string']

		try:
			result = re.sub(r'[\r\n\t]', "", html)
			result, other = re.search("<div>\s*<b>.*?</b></div><div>\s*(?:.*?<br/><br/>)?(.*?)</div>(?:<div class='others'>\s*(.*?)</div>)?", result).groups()
		except Exception as e:
			logger.exception("Error parsing html")
			result = None
		if not result or result is None or result == '':
			self.IRC.say(data[2], "\x02[UrbanDict]\x02 {0} has not yet been defined.".format(word))
			return None

		results = []
		for x in re.split("<br/>", result):
			if x == " " or x == "":
				continue
			x = x.replace('&quot;', '"').replace('<b>', '\x02').replace('</b>', '\x02').replace('<br/>', '')
			results.append(x)
			self.IRC.say(data[2], "\x02[UrbanDict]\x02 {0}: {1}".format(word, x))
		Locker.Lock()
		self.addWordToCache(word.lower(), " ".join(results))

	def Load(self):
		self.Parser.hookCommand("PRIVMSG", self.__name__, {"^@ud .*?$": self.Main})

	def Unload(self):
		pass
