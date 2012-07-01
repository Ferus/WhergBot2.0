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
		f = data[4] if len(data) >=4 and data[4] in self.Files else choice(self.Files)
		with open("{0}/{1}".format(self.Dir, f)) as _f:
			for line in _f.readlines():
				try:
					self.IRC.say(data[2], line)
				except UnicodeDecodeError:
					pass
		return

	def Load(self):
		self.Parser.hookCommand('PRIVMSG', "^@matix", self.Matix)
		self.Parser.loadedPlugins[self.__name__].append(Settings)
		self.Parser.loadedPlugins[self.__name__].append(self.Load)
		self.Parser.loadedPlugins[self.__name__].append(self.Unload)
		self.Parser.loadedPlugins[self.__name__].append(self.Reload)

	def Unload(self):
		pass
	def Reload(self):
		pass


