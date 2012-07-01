#!/usr/bin/env python
from random import choice

from .Settings import Settings

class Main(object):
	def __init__(self, Name, Parser):
		self.__name__ = Name
		self.Parser = Parser
		self.IRC = self.Parser.IRC
		
		self.ToldFile = Settings.get('ToldFile', 'Plugins/Told/Told.txt')
		with open(self.ToldFile, 'r') as Tolds:
			self.ToldList = Tolds.read().splitlines()

	def ReturnTold(self, data):
		 self.IRC.say(data[2], choice(self.ToldList))

	def Load(self):
		self.Parser.hookCommand('PRIVMSG', '^@told$', self.ReturnTold)
		self.Parser.loadedPlugins[self.__name__].append(Settings)
		self.Parser.loadedPlugins[self.__name__].append(self.Load)
		self.Parser.loadedPlugins[self.__name__].append(self.Unload)
		self.Parser.loadedPlugins[self.__name__].append(self.Reload)

	def Unload(self):
		pass
	def Reload(self):
		pass
