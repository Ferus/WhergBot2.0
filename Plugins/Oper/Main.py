#!/usr/bin/env python
import logging
from .Settings import Settings

logger = logging.getLogger("Oper")

class Main(object):
	def __init__(self, Name, Parser):
		self.__name__ = Name
		self.Parser = Parser
		self.IRC = self.Parser.IRC
		self.user = Settings.get(self.Parser.Connection.__name__)['user']
		self.password = Settings.get(self.Parser.Connection.__name__)['password']

	def Oper(self):
		logger.info("Opering up!")
		if hasattr(self.IRC, "oper"):
			self.IRC.oper(self.user, self.password)

	def Load(self):
		self.Parser.onConnect(self.Oper)
	def Unload(self):
		pass
	def Reload(self):
		pass

