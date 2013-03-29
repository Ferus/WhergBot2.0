#!/usr/bin/env python

#Google calculator.
import re
import json
import requests

class Main(object):
	def __init__(self, Name, Parser):
		self.__name__ = Name
		self.Parser = Parser
		self.IRC = self.Parser.IRC
		self.overrides = {"average penis size": "that feel when only seven inch penis"}

	def Calculate(self, data):
		calc = " ".join(data[4:])
		if calc in self.overrides:
			self.IRC.say(data[2], "\x02[Calculator]\x02 {0}: {1}".format(data[0].split("!")[0], self.overrides[calc]))
			return
		h = requests.get("http://www.google.com/ig/calculator", params={"q":calc})
		if h.status_code != 200:
			h.raise_for_status()
		h = re.sub("(\w+):", '"\\1" :', h.text)
		try:
			h = json.loads(h)
		except ValueError:
			return
		if h['error'] != '':
			self.IRC.say(data[2], "\x02[Calculator]\x02 Error running {0}".format(calc))
			return
		question = re.sub("(\d{1,3})\s(?=\d{3})", "\\1,", h['lhs'])
		answer = re.sub("(\d{1,3})\s(?=\d{3})", "\\1,", h['rhs'])
		self.IRC.say(data[2], "\x02[Calculator]\x02 {0}: {1} = {2}".format(data[0].split("!")[0], question, answer))

	def Load(self):
		self.Parser.hookCommand('PRIVMSG', self.__name__, {"^@calc .+$": self.Calculate})

	def Unload(self):
		del self.Parser.Commands['PRIVMSG'][1]["Calculator"]
	def Reload(self):
		pass
