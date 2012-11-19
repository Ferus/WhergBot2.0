#!/usr/bin/env python
from random import choice
from .Settings import Settings

class Main(object):
	def __init__(self, Name, Parser):
		self.__name__ = Name
		self.Parser = Parser
		self.IRC = self.Parser.IRC

	def Random(self, data):
		data = data[4].split(',')
		self.IRC.say(choice(data))

	def Load(self):
		self.Parser.hookCommand('PRIVMSG', self.__name__, {"^@random", self.Random})

	def Unload(self):
		pass
	def Reload(self):
		pass
