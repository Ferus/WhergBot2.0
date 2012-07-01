#!/usr/bin/env python

import requests

from .Settings import Settings
from Parser import Locker
Locker = Locker(Settings.get('locktime', 5))

class Main(object):
	def __init__(self, Name, Parser):
		self.__name__ = Name
		self.Parser = Parser
		self.IRC = self.Parser.IRC
	
	def generateInsult(self, data):
		if Locker.Locked:
			self.IRC.notice(data[0].split('!')[0], "Wait a bit longer, faggot.")
			return None

		html = requests.get("http://insultgenerator.org/")
		if html.status_code != 200:
			self.IRC.say(data[2], "{0}: I couldn't connect to InsultGenerator faggot.".format(data[0].split('!')[0]))
			
		insult = html.content.split("<TR align=center><TD>")[1].split("</TD></TR>")[0]
		try:
			self.IRC.say(data[2], "{0}: {1}".format(data[4], insult))
		except IndexError:
			self.IRC.say(data[2], "{0}: {1}".format(data[0].split('!')[0], insult))
		Locker.Lock()

	def Load(self):
		self.Parser.hookCommand('PRIVMSG', "^@insult(?: \W+)?", self.generateInsult)
		self.Parser.loadedPlugins[self.__name__].append(Settings)
		self.Parser.loadedPlugins[self.__name__].append(self.Load)
		self.Parser.loadedPlugins[self.__name__].append(self.Unload)
		self.Parser.loadedPlugins[self.__name__].append(self.Reload)

	def Unload(self):
		pass
	def Reload(self):
		pass
