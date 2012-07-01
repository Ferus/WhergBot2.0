#!/usr/bin/python2
from random import choice
from .Settings import Settings
class Main(object):
	def __init__(self, Name, Parser):
		self.__name__ = Name
		self.Parser = Parser
		self.IRC = self.Parser.IRC
		self.replies = Settings.get('replies')

	def Ball(self, data):
		if not data[4:]:
			self.IRC.notice(data[0].split('!')[0], "Ask me a question bud!")
		else:
			self.IRC.say(data[2], "{0}: {1}".format(data[0].split('!')[0], choice(self.replies)))

	def Load(self):
		self.Parser.hookCommand('PRIVMSG', "^@8ball", self.Ball)
		self.Parser.loadedPlugins[self.__name__].append(Settings)
		self.Parser.loadedPlugins[self.__name__].append(self.Load)
		self.Parser.loadedPlugins[self.__name__].append(self.Unload)
		self.Parser.loadedPlugins[self.__name__].append(self.Reload)
	
	def Unload(self):
		pass
	def Reload(self):
		pass

