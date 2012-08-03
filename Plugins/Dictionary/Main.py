#!/usr/bin/env python
try:
	import wordnik
except ImportError:
	raise Exception("* [Dictionary] Please install the wordnik module to use the Dictionary plugin.")

from .Settings import Settings
from Parser import Locker
Lock = Locker(5)

class Main(object):
	def __init__(self, Name, Parser):
		self.__name__ = Name
		self.Parser = Parser
		self.IRC = self.Parser.IRC

		self.APIkey = Settings.get("APIkey")
		print("* [Dictionary] Using API Key '{0}'".format(self.APIkey))
		self.Word = wordnik.Wordnik(api_key=self.APIkey)

	def getDefinitions(self, data):
		if Lock.Locked:
			self.IRC.notice(data[0].split('!')[0], "Please wait a little longer before using this command again.")
			return None
		w = " ".join(data[4:])
		defs = []
		deflist = self.Word.word_get_definitions(w)[0:3]
		numdefs = len(deflist)
		for x in deflist:
			defs.append(x['text'])

		if numdefs == 0:
			self.IRC.say(data[2],"\x02[WordNik]\x02 I didn't find any definitions for '{0}'.".format(w))
		elif numdefs == 1:
			self.IRC.say(data[2], "\x02[WordNik]\x02 I found one definition for '{0}'.".format(w))
			self.IRC.say(data[2], "\x02[WordNik]\x02 {0}: {1}".format(w, defs[0]))
		else:
			self.IRC.say(data[2], "\x02[WordNik]\x02 I found {0} definitions for '{1}'.".format(numdefs, w))
			while len(defs) != 0:
				self.IRC.say(data[2], "\x02[WordNik]\x02 {0}: {1}".format(w, defs.pop(0)))
		Lock.Lock()
	
	def Load(self):
		self.Parser.hookCommand('PRIVMSG', "^@def( .*?)?$", self.getDefinitions)
		self.Parser.hookPlugin(self.__name__, Settings, self.Load, self.Unload, self.Reload)
	def Unload(self):
		pass
	def Reload(self):
		pass
