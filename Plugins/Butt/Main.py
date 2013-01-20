#!/usr/bin/env python

import random
random.seed("".join(random.choice("qwertyuiopasdfghjklzxcvbnm") for x in range(random.randint(10, 100))))
from .Settings import Settings

class Main(object):
	def __init__(self, Name, Parser):
		self.__name__ = Name
		self.Parser = Parser
		self.IRC = self.Parser.IRC

	def Butt(self, data):
		if data[2] not in Settings.get("allowedChans"):
			return None
		if random.randint(0, 100) > Settings.get("replyrate"):
			return None
		d = " ".join(data[3:])[1:].split()
		if len(d) > 3:
			for x in range(random.randint(1, Settings.get("maxreplace"))):
				word = random.choice(list(set(d)))
				for index, item in enumerate(d):
					if item == word:
						d[index] = "butt"
						break
		else:
			d.insert(random.randint(0, len(d)), "butt")
		self.IRC.say(data[2], " ".join(d))

	def Load(self):
		self.Parser.hookCommand('PRIVMSG', self.__name__, {".*": self.Butt})

	def Unload(self):
		del self.Parser.Commands['PRIVMSG'][1][self.__name__]
