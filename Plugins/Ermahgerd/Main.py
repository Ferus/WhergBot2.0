#!/usr/bin/env python

import requests
from .Settings import Settings

from Parser import Locker
Locker = Locker(3)

class Main(object):
	def __init__(self, Name, Parser):
		self.__name__ = Name
		self.Parser = Parser
		self.IRC = self.Parser.IRC

	def Get(self, message):
		r = requests.get("http://199.19.116.75/ermahgerd.php?text={0}".format(message.replace(" ", "%20")))
		if r.status_code != 200:
			r.raise_for_status()
		return r.content

	def Send(self, data):
		if Locker.Locked:
			self.IRC.say(data[2], "Please wait a little longer and try again.")
			return
		message = " ".join(data[4:])
		try:
			m = self.Get(message)
			self.IRC.say(data[2], data[0].split("!")[0]+": "+m)
		except Exception as e:
			self.IRC.say(data[2], e.args)

	def Load(self):
		self.Parser.hookCommand('PRIVMSG', "^@ermahgerd \w+", self.Send)
		self.Parser.hookPlugin(self.__name__, Settings, self.Load, self.Unload, self.Reload)

	def Unload(self):
		del self.Parser.loadedPlugins[self.__name__]
	def Reload(self):
		pass
