#!/usr/bin/env python
from time import strftime

import Config
from .Settings import Settings

class Service(object):
	def __init__(self, Parser, IRC, name):
		self.IRC = IRC
		self.__name__ = name

	def Send(self, Message):
		self.IRC.say(self.__name__, Message)

class NickServ(Service):
	def __init__(self, Parser, IRC):
		self.Parser = Parser
		self.IRC = IRC
		Service.__init__(self, self.Parser, self.IRC, "NickServ")

	def Register(self):
		pass

	def Group(self):
		pass

	def Glist(self):
		pass

	def Identify(self):
		self.Send("Identify {0}".format(Settings.get("password")))
		print("{0} {1}: Authenticating to NickServ".format(strftime(Config.Global['timeformat']), self.Parser.Connection.__name__))

	def Access(self):
		pass

	def Set(self):
		pass

	def Drop(self):
		pass

	def Recover(self):
		pass

	def Release(self):
		pass

	def Ghost(self):
		self.Send("Ghost {0}".format(Settings.get("password")))

	def Alist(self):
		pass

	def Info(self):
		pass

	def Logout(self):
		pass

	def Status(self):
		pass

	def Update(self):
		self.Send("Update")

class Umodes(object):
	def __init__(self, Parser, IRC):
		self.Parser = Parser
		self.IRC = IRC

	def setMode(self):
		self.IRC.mode(self.Parser.Connection.Config.get('nick'), Settings.get('modes'))


class Main(object):
	def __init__(self, Name, Parser):
		self.__name__ = Name
		self.Parser = Parser
		self.IRC = self.Parser.IRC

		self.NickServ = NickServ(self.Parser, self.IRC)
		self.Umode = Umodes(self.Parser, self.IRC)

	def Load(self):
		self.Parser.onConnect(self.NickServ.Identify)
		self.Parser.onConnect(self.Umode.setMode)

		self.Parser.hookPlugin(self.__name__, Settings, self.Load, self.Unload, self.Reload)
	def Unload(self):
		pass
	def Reload(self):
		pass
