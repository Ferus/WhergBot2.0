#!/usr/bin/env python

import Config
from .Settings import Settings

class Main(object):
	def __init__(self, Name, Parser):
		self.__name__ = Name
		self.Parser = Parser
		self.IRC = self.Parser.IRC

	def Killed(self, data):
		pass
	def Pingout(self, data):
		pass
	def ioError(self, data):
		pass

	def Load(self):
		# old
		#self.Parser.Commands['QUIT'][1].append((Settings.get("Killed"), self.Killed))
		#self.Parser.Commands['QUIT'][1].append((Settings.get("Pingout"), self.Pingout))
		#self.Parser.Commands['QUIT'][1].append((Settings.get("ioError"), self.ioError))
		self.Parser.hookPlugin(self.__name__, Settings, self.Load, self.Unload, self.Reload)

	def Unload(self):
		del self.Parser.loadedPlugins[self.__name__]
	def Reload(self):
		pass
