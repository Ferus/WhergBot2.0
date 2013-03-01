#!/usr/bin/env python
from datetime import datetime
import logging

from .Settings import Settings
from .lastseen import Seen
from .relativeDates import timesince

logger = logging.getLogger("LastSeen")

class Main(object):
	def __init__(self, Name, Parser):
		self.__name__ = Name
		self.Parser = Parser
		self.IRC = self.Parser.IRC
		self.Seen = Seen(Settings.get("database", ":memory:"))

	def add(self, data):
		# Dont log pm's
		if not data[2].startswith("#"):
			return None
		# Dont log blacklisted chans
		if data[2] in Settings.get("blacklist"):
			return None
		nick = data[0].split("!")[0]
		chan = data[2]
		msg = " ".join(data[3:])[1:]
		self.Seen.addLastSeen(nick, chan, msg)

	def seen(self, data):
		s = self.Seen.getLastSeen(data[4])
		if not s:
			self.IRC.say(data[2], "I don't know who \x02{0}\x02 is.".format(data[4]))
			return
		nick, chan, msg, timestamp = s
		timestamp = datetime.fromtimestamp(timestamp)
		timestamp = timesince(timestamp)
		self.IRC.say(data[2], "\x02{0}\x02 was last seen in \x02{1}\x02 (\x02{2}\x02) about \x02{3}\x02 ago".format(
			nick, chan, msg, timestamp))

	def Load(self):
		self.Parser.hookCommand("PRIVMSG", self.__name__, {".*": self.add
			,"^@seen \S+$": self.seen})
		# QUITS too?

	def Unload(self):
		pass
