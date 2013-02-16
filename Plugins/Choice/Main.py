#!/usr/bin/env python
import random

class Main(object):
	def __init__(self, Name, Parser):
		self.__name__ = Name
		self.Parser = Parser
		self.IRC = self.Parser.IRC

	def Random(self, data):
		self.IRC.say(data[2], random.choice(data[4].split(",")))

	def Load(self):
		self.Parser.hookCommand('PRIVMSG', self.__name__, {"^@random": self.Random})

	def Unload(self):
		pass
	def Reload(self):
		pass
