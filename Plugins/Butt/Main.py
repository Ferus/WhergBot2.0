#!/usr/bin/env python

import random
import re
from .Settings import Settings

class Main(object):
	def __init__(self, Name, Parser):
		self.__name__ = Name
		self.Parser = Parser
		self.IRC = self.Parser.IRC

	def Butt(self, data):
		if not random.randint(0, 100) > Settings.get("replyrate"):
			return None
		d = " ".join(data[3:])[1:]
		for x in range(random.randint(1, Settings.get("maxreplace"))):
			d = re.sub(" "+random.choice(list(set(d.split())))+" ", " butt ", d, count=1)
		self.IRC.say(data[2], d)

	def Load(self):
		self.Parser.hookCommand('PRIVMSG', self.__name__, {".*": self.Butt})

	def Unload(self):
		del self.Parser.Commands['PRIVMSG'][1][self.__name__]
