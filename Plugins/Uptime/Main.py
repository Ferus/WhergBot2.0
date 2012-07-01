#!/usr/bin/env python

import datetime
import time

class Main(object):
	def __init__(self, Name, Parser):
		self.__name__ = Name
		self.Parser = Parser
		self.IRC = self.Parser.IRC
		
	def Uptime(self, data):
		uptime = time.time() - self.Parser.Connection.__time__
		uptime = datetime.timedelta(seconds=uptime)
		self.IRC.say(data[2], "Current uptime is: {0}.".format(str(uptime).split('.')[0].zfill(8)))

	def Load(self):
		self.Parser.hookCommand("PRIVMSG", "^@uptime$", self.Uptime)
		self.Parser.loadedPlugins[self.__name__].append(None)
		self.Parser.loadedPlugins[self.__name__].append(self.Load)
		self.Parser.loadedPlugins[self.__name__].append(self.Unload)
		self.Parser.loadedPlugins[self.__name__].append(self.Reload)

	def Unload(self):
		pass
	def Reload(self):
		pass
