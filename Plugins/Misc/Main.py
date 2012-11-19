#!/usr/bin/env python
from threading import Timer
from random import randint
import requests
import re

from .Settings import Settings

class Main(object):
	def __init__(self, Name, Parser):
		self.__name__ = Name
		self.Parser = Parser
		self.IRC = self.Parser.IRC

	def Oven(self, data):
		target = data[4] if data[4] else data[0].split('!')[0]
		self.IRC.action(data[2], "prepares his ovens")
		t = Timer(randint(Settings.get('ovenmintime'), Settings.get('ovenmaxtime')), self.IRC.action, (data[2], "ovens {0}".format(target)))
		t.daemon = True
		t.start()

	def Next(self, data):
		self.IRC.say(data[2], "Another satisfied customer! Next!")

	def Bacon(self, data):
		target = data[4] if data[4] else 'Ferus'
		self.IRC.action(data[2], "cooks up some fancy bacon for {0}".format(target))

	def Hug(self, data):
		if data[0] in Settings.get('hugallowed'):
			self.IRC.action(data[2], "hugs {0}.".format(data[0].split('!')[0]))
		else:
			self.IRC.action(data[2], "kicks {0} in the balls for not being a man.".format(data[0].split('!')[0]))

	def isup(self, data):
		if not data[4]:
			return None
		site = data[4]
		html = requests.get("http://www.isup.me/{0}".format(site))
		if html.status_code != 200:
			self.IRC.say(data[2], "I couldn't connect to isup.me.")
			return None
		html = re.sub("\t|\n", "", html.text)
		h = re.findall("<div id=\"container\">(.*?)<p>.*?</div>", html)[0]
		h = re.sub("<a href=\".*?\" class=\"domain\">", "", h)
		h = re.sub("</a>(:?</span>)?", "", h)
		h = re.sub("\s{2,}", " ", h).strip(" ")
		self.IRC.say(data[2], "\x02[ISUP]\x02 {0}".format(h))

	def HelloWorld(self, data):
		self.IRC.say(data[2], "Hello World!")


	def Load(self):
		self.Parser.hookCommand("PRIVMSG", self.__name__
			,{'^@oven(?: .*?)?$': self.Oven
			,'^@next$': self.Next
			,'^@bacon(?: .*?)?$': self.Bacon
			,'(?:^|\s+);[_-~\.]{1};(?:\s|$)': self.Hug
			,'^@isup(?: .*?)?$': self.isup
			,'^@h': self.HelloWorld
			}
		)

	def Unload(self):
		del self.Parser.Commands["PRIVMSG"][1][self.__name__]
	def Reload(self):
		pass
