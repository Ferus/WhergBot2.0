#!/usr/bin/env python
from time import sleep
from threading import Thread
import logging
from .Settings import Settings

logger = logging.getLogger("Oper")

class Main(object):
	def __init__(self, Name, Parser):
		self.__name__ = Name
		self.Parser = Parser
		self.IRC = self.Parser.IRC

	def Oper(self):
		logger.info("Opering up!")
		if hasattr(self.IRC, "oper"):
			self.IRC.oper(Settings['user'], Settings['password'])

	def Load(self):
		self.Parser.onConnect(self.Oper)
	def Unload(self):
		pass
	def Reload(self):
		pass

