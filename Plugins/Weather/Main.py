#!/usr/bin/env python
#
# Weather plugin, uses thefuckingweather.com
#
from . import TheFuckingWeather
from .Settings import Settings

class Main(object):
	def __init__(self, Name, Parser):
		self.__name__ = Name
		self.Parser = Parser
		self.IRC = self.Parser.IRC

	def Weather(self, data):
		zipcode = data[4]
		weather = TheFuckingWeather.getWeather(zipcode)
		self.IRC.say(data[2], "\x02[TheFuckingWeather]\x02 {0}: {1}".format(data[0].split("!")[0], weather))

	def Load(self):
		self.Parser.hookCommand('PRIVMSG', self.__name__, {"^@weather \d{5}": self.Weather})

	def Unload(self):
		del self.Parser.loadedPlugins[self.__name__]
	def Reload(self):
		pass


