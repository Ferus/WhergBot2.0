#!/usr/bin/env python
import re

Regex = "NickServ: .+!.+@.+ identified for nick (stal|WhergBot|Eutectic|xqks|learningcode|\[^_^\]|blam|Wolfie|Hunter|diath|Ferus)"

class Main(object):
	def __init__(self, Name, Parser):
		self.__name__ = Name
		self.Parser = Parser
		self.IRC = self.Parser.IRC

	def Flood(self, data):
		d = " ".join(data[3:])[1:]
		h = re.match(Regex, d).groups()[0]
		if h:
			self.IRC.say("OperServ", "flood {0}".format(h))
			self.IRC.say("#services", "Used OS FLOOD on {0}".format(h))

	def Load(self):
		self.Parser.hookCommand("PRIVMSG", self.__name__, {Regex: self.Flood})
	def Unload(self):
		del self.Parser.Commands['PRIVMSG'][1][self.__name__]
