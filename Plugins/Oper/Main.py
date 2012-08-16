#!/usr/bin/env python
from time import sleep
from threading import Thread
from .Settings import Settings

class Main(object):
	def __init__(self, Name, Parser):
		self.__name__ = Name
		self.Parser = Parser
		self.IRC = self.Parser.IRC

	def Oper(self):
		print(">>> [Oper] Opering up!")
		if hasattr(self.IRC, "oper"):
			self.IRC.oper(Settings['user'], Settings['password'])
	
	def _KillAnnoyHelper(self, data):
		# @killannoy 100 5 Eutectic Reason blah blah blah
		if not hasattr(self.IRC, "kill"):
			return None
		if not data[4].isdigit() and not data[5].isdigit():
			return None
		
		x = int(data[4])
		while x != 0:
			t = Thread(target=self.IRC.kill, args=(data[6], " ".join(data[7:])))
			t.daemon = True
			t.start()
			x-=1
			sleep(int(data[5]))
	def KillAnnoy(self, data):
		if data[0] not in Settings.get("allowed"):
			return None
		print("True")
		t = Thread(target=self._KillAnnoyHelper, args=(data,))
		t.daemon = True
		t.start()

	def Load(self):
		self.Parser.onConnect(self.Oper)
		self.Parser.hookCommand("PRIVMSG", "^@killannoy \d{1,} \d{1,} \w+ \w.+$", self.KillAnnoy)
		self.Parser.hookPlugin(self.__name__, Settings, self.Load, self.Unload, self.Reload)
	def Unload(self):
		pass
	def Reload(self):
		pass

