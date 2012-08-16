#!/usr/bin/env python
try:
	from wordnik.api.APIClient import APIClient
	from wordnik.api.WordAPI import WordAPI
	import wordnik.model
except ImportError:
	raise Exception("* [Wordnik] Please install the wordnik module to use the Dictionary plugin.")

from .Settings import Settings
from Parser import Locker
Lock = Locker(5)

class Main(object):
	def __init__(self, Name, Parser):
		self.__name__ = Name
		self.Parser = Parser
		self.IRC = self.Parser.IRC

		self.APIkey = Settings.get("APIkey")
		print(">>> [Wordnik => __init__] Using API Key '{0}'".format(self.APIkey))
		self.Client = APIClient(self.APIkey, 'http://api.wordnik.com/v4')
		self.wordAPI = WordAPI(self.Client)

	def getDefinitions(self, data):
		if Lock.Locked:
			self.IRC.notice(data[0].split('!')[0], "Please wait a little longer before using this command again.")
			return None
		w = " ".join(data[4:])

		input = wordnik.model.WordDefinitionsInput.WordDefinitionsInput()
		input.word = w
		input.limit = 3
		defs = self.wordAPI.getDefinitions(input)

		if len(defs) == 0:
			self.IRC.say(data[2],"\x02[WordNik]\x02 I didn't find any definitions for '{0}'.".format(w))
		elif len(defs) == 1:
			self.IRC.say(data[2], "\x02[WordNik]\x02 I found one definition for '{0}'.".format(w))
			self.IRC.say(data[2], "\x02[WordNik]\x02 {0}: {1}".format(w, defs[0].text))
		else:
			self.IRC.say(data[2], "\x02[WordNik]\x02 I found {0} definitions for '{1}'.".format(len(defs), w))
			for x in defs:
				self.IRC.say(data[2], "\x02[WordNik]\x02 {0}: {1}".format(w, x.text))
		Lock.Lock()
	
	def Load(self):
		self.Parser.hookCommand('PRIVMSG', "^@def( .*?)?$", self.getDefinitions)
		self.Parser.hookPlugin(self.__name__, Settings, self.Load, self.Unload, self.Reload)
	def Unload(self):
		pass
	def Reload(self):
		pass
