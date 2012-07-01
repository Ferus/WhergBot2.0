#!/usr/bin/env python
import re

from .Settings import Settings

class Main(object):
	def __init__(self, Name, Parser):
		self.__name__ = Name
		self.Parser = Parser
		self.IRC = self.Parser.IRC

		self.Topic = ''
		self.NamesFile = 'UboaNames.txt'
		try:
			with open(self.NamesFile, 'r') as NF:
				self.Names = [x.split(':') for x in NF.read().splitlines()]
		except IOError:
			with open(self.NamesFile, 'w') as NF:
				NF.close()
			self.Names = []

	def NamesLength(self):
		return len(self.Names)

	def AddNick(self, Name, Nick):
		Settings['nicks'].append([Name, Nick])
		with open(self.NamesFile, 'w') as NF:
			NF.write(Name+":"+Nick+"\r\n")
		return True

	def RemoveNick(self, Name='', Nick=''):
		if not Name and if not Nick:
			return False
		for Namelist in self.Names:
			if Name:
				if Name == Namelist[0]:
					self.Names.remove(Namelist)
			else:
				if Nick == Namelist[1]:
					self.Names.remove(Namelist)
	
	def WriteNames(self):
		with open(self.NamesFile, 'wr') as NF:
			Nameslist = [x.split(':') for x in NF.read().splitlines()]
			for x in self.Names:
				if x[0] not in [y[0] for y in Nameslist]:
					NF.write(x[0]+":"+x[1]+"\r\n")

	def SetTopic(self, topic=''):
		pass
	



# Default to player name if no nick is set
# onConnect -> append name
# onDisconnect -> remove name
# onTopic -> update topic
# onPlayers -> update players
