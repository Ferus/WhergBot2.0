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
			nick = data[0].split("!")[0]
			self.IRC.say(data[2], "\x02{0}\x02 has to fap to \x02{1}\x02!".format(nick, choice(Settings['faps'].format(nick=nick))))
			Lock.Lock()
		else:
			self.IRC.notice(data[0].split("!")[0], "Please wait a little longer before using this command again.")

	def Load(self):
		self.Parser.hookCommand('PRIVMSG', "^@fapget$", self.Fapget)
		self.Parser.hookPlugin(self.__name__, Settings, self.Load, self.Unload, self.Reload)

	def Unload(self):
		pass
	def Reload(self):
		pass

