#!/usr/bin/env python
from random import choice

from .Settings import Settings
from Parser import Locker
Lock = Locker(5)

class Main(object):
	def __init__(self, Name, Parser):
		self.__name__ = Name
		self.Parser = Parser
		self.IRC = self.Parser.IRC

	def Fapget(self, data):
		if not Lock.Locked:
			self.IRC.say(data[2], "\x02{0}\x02 has to fap to \x02{1}\x02!".format(data[0].split("!")[0], choice(Settings['faps'])))
			Lock.Lock()
		else:
			self.IRC.notice(data[0].split("!")[0], "Please wait a little longer before using this command again.")

	def Load(self):
		self.Parser.hookCommand('PRIVMSG', "^@fapget$", self.Fapget)
		self.Parser.loadedPlugins[self.__name__].append(Settings)
		self.Parser.loadedPlugins[self.__name__].append(self.Load)
		self.Parser.loadedPlugins[self.__name__].append(self.Unload)
		self.Parser.loadedPlugins[self.__name__].append(self.Reload)

	def Unload(self):
		pass
	def Reload(self):
		pass
	
