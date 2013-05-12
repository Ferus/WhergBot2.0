#!/usr/bin/env python

import requests
from urllib.parse import quote
import re
import json
import sqlite3
import time
import threading
import logging
logger = logging.getLogger("UrbanDictionary")

from Parser import Locker
Locker = Locker(5)
from .Settings import Settings

class Main(object):
	def __init__(self, Name, Parser):
		self.__name__ = Name
		self.Parser = Parser
		self.IRC = self.Parser.IRC

		self.Connection = sqlite3.connect(Settings.get("CacheDB", "Plugins/UrbanDictionary/Cache.sql3"), check_same_thread = False)
		self.Cursor = self.Connection.cursor()
		self.Cursor.execute("""CREATE TABLE IF NOT EXISTS urbandictionary
			(id INTEGER PRIMARY KEY AUTOINCREMENT
			,word TEXT
			,definition TEXT
			,thumbs_up INTEGER
			,thumbs_down INTEGER
			,permalink TEXT
			,timestamp DATE DEFAULT (strftime('%s', 'now'))
			)""")
		self.cacheTime = Settings.get("cacheTime", 60*60*24*7) # One week
		self.purgeCache()

	def checkCacheForDef(self, word):
		logger.info("Checking cache for info")
		row = self.Cursor.execute("SELECT definition, thumbs_up, thumbs_down, permalink, timestamp FROM urbandictionary WHERE word=?", [word.lower()])
		definition = row.fetchone()
		if definition:
			if int(time.time()) - definition[-1] > self.cacheTime:
				logger.info("Timestamp exceeded set cached time ({0} hours). Refreshing.".format(self.cacheTime/3600))
				return None
			return definition
		else:
			return None

	def addWordToCache(self, word, definition, thumbs_up, thumbs_down, permalink):
		if self.Cursor.execute("SELECT COUNT(*) FROM urbandictionary WHERE word=?", [word.lower()]).fetchone()[0] != 0:
			self.Cursor.execute("UPDATE urbandictionary SET definition=?, thumbs_up=?, thumbs_down=?, permalink=?, timestamp=strftime('%s', 'now') WHERE word=?",
				[definition, thumbs_up, thumbs_down, permalink, word.lower()])
		else:
			self.Cursor.execute("INSERT INTO urbandictionary (word, definition, thumbs_up, thumbs_down, permalink) VALUES (?, ?, ?, ?, ?)",
				[word.lower(), definition, thumbs_up, thumbs_down, permalink])
		self.Connection.commit()

	def purgeCache(self, data = None):
		if data:
			if data[0] not in Settings.get("purgeAllowed", []):
				return None
			self.IRC.say(data[2], '\x02[UrbanDict]\x02 Purging all cached entries older than \x02{0}\x02 seconds.'.format(self.cacheTime))
		self.Cursor.execute("DELETE FROM urbandictionary WHERE strftime('%s', 'now') - timestamp > ?", [self.cacheTime])


	def Main(self, data):
		if Locker.Locked:
			self.IRC.notice(data[0].split("!")[0], "Please wait a little bit longer before using this command.")
			return None
		word = ' '.join(data[4:])
		definition = self.checkCacheForDef(word)
		if definition is not None:
			logger.info("Sending cached word.")
			self.IRC.say(data[2], "\x02[UrbanDict]\x02 {0}: {1} [\x02{2} ↑\x02/\x02{3} ↓\x02] - {4}".format(
				word, definition[0], definition[1], definition[2], definition[3]))
			Locker.Lock()
			return None

		try:
			logger.info("Polling UrbanDictionary.")
			html = requests.get("http://api.urbandictionary.com/v0/define?term={0}".format(quote(word)))
		except (requests.HTTPError, requests.ConnectionError) as e:
			logger.exception("Failed to connect.")
			self.IRC.say(data[2], "\x02[UrbanDict]\x02 Failed to connect to Urban Dictionary.")
			return None
		result = json.loads(html.text)
		if result['result_type'] != "exact":
			logger.info("Word not defined.")
			self.IRC.say(data[2], "\x02[UrbanDict]\x02 {0} has not yet been defined.".format(word))
			return None

		def clean(definition):
			definition = re.sub("[\r|\n]+", " ", definition)
			definition = definition.replace("[", "\x02").replace("]", "\x02")
			if len(definition) > 320:
				definition = definition[:320]+"..."
			definition = re.sub("[\t|\s]+", " ", definition)
			return definition

		result = result['list'][0]
		definition = clean(result['definition'])
		thumbs_up = int(result['thumbs_up'])
		thumbs_down = int(result['thumbs_down'])
		permalink = result['permalink']
		self.IRC.say(data[2], "\x02[UrbanDict]\x02 {0}: {1} [\x02{2} ↑\x02/\x02{3} ↓\x02] - {4}".format(
			word, definition, thumbs_up, thumbs_down, permalink))
		Locker.Lock()
		self.addWordToCache(word, definition, thumbs_up, thumbs_down, permalink)

	def Load(self):
		self.Parser.hookCommand("PRIVMSG", self.__name__, {"^@ud .*?$": self.Main
			,"^@ud\.purge$": self.purgeCache
			})

	def Unload(self):
		self.purgeCache()
		self.Connection.commit()
		self.Connection.close()

