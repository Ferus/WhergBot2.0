#!/usr/bin/env python
from .Settings import Settings

class Main(object):
	def __init__(self, Name, Parser):
		self.__name__ = Name
		self.Parser = Parser
		self.IRC = self.Parser.IRC

	def Join(self, data):
		if data[0] in Settings.get("allowed"):
			self.IRC.join(data[4])
	def Part(self, data):
		if data[0] in Settings.get("allowed"):
			self.IRC.part(data[4], " ".join(data[5:]))
	
	def RejoinOnKick(self, data):
		#u!i@h KICK #4chon WhergBot :lol
		if data[3] == self.IRC.getnick():
			self.IRC.join(data[2])

	def Load(self):
		self.Parser.hookCommand('PRIVMSG', "^@join #\w", self.Join)
		self.Parser.hookCommand('PRIVMSG', "^@part #\w(?: \w+)?", self.Part)
		self.Parser.hookCommand('KICK', ".*", self.RejoinOnKick)
		self.Parser.hookPlugin(self.__name__, Settings, self.Load, self.Unload, self.Reload)
	def Unload(self):
		pass
	def Reload(self):
		pass

