#!/usr/bin/env python
import requests, re

from .Settings import Settings
from Parser import Locker
Lock = Locker(5)

class Main(object):
	def __init__(self, Name, Parser):
		self.__name__ = Name
		self.Parser = Parser
		self.IRC = self.Parser.IRC

		self.fml_Generator = self.fml()

	def get_fml(self):
		fml_db = []
		url = "http://fmylife.com/random"
		_html = requests.get(url)
		if _html.status_code != 200:
			return False #Error
		_html = _html.text #Page HTML
		comp = "<div class=\"post article\" id=\"[0-9]{1,}\"><p><a href=\"\/[a-zA-Z0-9_-]{1,}\/[0-9]{1,}\" class=\"fmllink\">.*?</a></p>"
		tmp = re.findall(comp, _html)
		for x in tmp:
			x = re.sub("<div class=\"post article\" id=\"[0-9]{1,}\"><p><a href=\"\/[a-zA-Z0-9_-]{1,}\/[0-9]{1,}\" class=\"fmllink\">", "", x)
			x = re.sub("</a><a href=\"\/[a-zA-Z0-9_-]{1,}\/[0-9]{1,}\" class=\"fmllink\">", "", x)
			x = re.sub("</a></p>", "", x)
			fml_db.append(x)
		return fml_db

	def fml(self):
		fml_db = []
		while True:
			if not fml_db:
				print("* [FML] Getting more FML's.")
				fml_db = self.get_fml()
			_fml = fml_db.pop()
			yield "\x02[FML]\x02 {0}".format(_fml)

	def return_fml(self, data):
		try:
			if not Lock.Locked:
				self.IRC.say(data[2], next(self.fml_Generator))
				Lock.Lock()
			else:
				self.IRC.notice(data[0].split('!')[0], "Please wait a little longer before using this command again.")
		except Exception as e:
			print("* [FML] Error:\n* [FML] {0}".format(str(e)))

	def Load(self):
		self.Parser.hookCommand('PRIVMSG', self.__name__, {"^@fml": self.return_fml})

	def Unload(self):
		pass

	def Reload(self):
		pass

