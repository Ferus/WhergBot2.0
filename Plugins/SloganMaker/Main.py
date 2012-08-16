#!/usr/bin/env python
import requests

from Parser import Locker
Locker = Locker(0)

from .Settings import Settings

def get_slogan(text):
	r = requests.post('http://www.sloganmaker.com/sloganmaker.php', data={'user':text})
	if r.status_code == 200:
		return "\x02[SloganMaker]\x02 {0}".format(r.text.split('<p>')[1].split('</p>')[0])
	else:
		print("* [SloganMaker] Error - Status Code {0}".format(r.status_code))
		return "\x02[SloganMaker]\x02 Error; Status Code {0}".format(r.status_code)

class Main(object):
	def __init__(self, Name, Parser):
		self.__name__ = Name
		self.Parser = Parser
		self.IRC = self.Parser.IRC

	def Slogan(self, data):
		try:
			if not Locker.Locked:
				self.IRC.say(data[2], get_slogan(" ".join(data[4:])))
				Locker.Lock()
			else:
				self.IRC.notice(data[0].split('!')[0], "Please wait a little longer before using this command again")
		except Exception as e:
			print("* [SloganMaker] Error:\n* [SloganMaker] {0}".format(str(e)))

	def Load(self):
		self.Parser.hookCommand("PRIVMSG", "^@slogan .*?$", self.Slogan)
		self.Parser.hookPlugin(self.__name__, Settings, self.Load, self.Unload, self.Reload)

	def Unload(self):
		pass
	def Reload(self):
		pass

