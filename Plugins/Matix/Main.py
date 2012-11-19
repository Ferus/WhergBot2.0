#!/usr/bin/env python
import os
from random import choice

import Config
from .Settings import Settings

class Main(object):
	def __init__(self, Name, Parser):
		self.__name__ = Name
		self.Parser = Parser
		self.IRC = self.Parser.IRC
		self.Dir = Settings.get("dir")
		self.Files = os.listdir(self.Dir)

	def Matix(self, data):
		if data[0] not in Settings['allowed']:
			return None
		try:
			File = data[4] if data[4] in self.Files else choice(self.Files)
		except IndexError:
			File = choice(self.Files)
		with open("{0}/{1}".format(self.Dir, File)) as f:
			try:
				for line in f.readlines():
					self.IRC.say(data[2], line)
			except UnicodeDecodeError:
				self.Files.remove(File)
				os.unlink(self.Dir + os.sep + File)
				self.IRC.say(data[2], "Removed invalid unicode file: {0}".format(File))

	def Load(self):
		self.Parser.hookCommand('PRIVMSG', self.__name__, {"^@matix": self.Matix})

	def Unload(self):
		pass
	def Reload(self):
		pass


