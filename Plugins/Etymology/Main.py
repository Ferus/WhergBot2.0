#!/usr/bin/env python

import re
import requests

from .Settings import Settings
from Parser import Locker
Locker = Locker(5)

class Main(object):
	def __init__(self, Name, Parser):
		self.__name__ = Name
		self.Parser = Parser
		self.IRC = self.Parser.IRC

	def Etymology(self, data):
		if Locker.Locked:
			self.IRC.notice(data[0].split('!')[0], "Please wait a little bit longer before using this command")
			return None
		word = " ".join(data[4:])
		if not word:
			self.IRC.notice(data[0], "Specify a word!")
			return None
		Origins = self.getWordEtymology(word)
		for h in Origins:
			self.IRC.say(data[2], "\x02[Etymology]\x02 {0} - {1}".format(word, h))

	def getWordEtymology(self, word):
		try:
			info = requests.get("http://www.etymonline.com/index.php?term={0}".format(word)).content
		except requests.HTTPError, e:
			return None
		info = re.sub("[\r\n\t]", "", info)
		try:
			info = re.findall("<dd class=\"highlight\">(.*?)<\/dd>", info)[0]
		except IndexError, e:
			return ["Word origin not found!"]

		Spans = re.findall("<span .*?>(.*?)<\/span>", info)
		for Span in Spans:
			info = re.sub("<span .*?>{0}<\/span>".format(Span), "\x02{0}\x02".format(Span), info)
	
		Links = re.findall("<a href=\".*?\" class=\".*?\">(.*?)</a>", info)
		for Link in Links:
			info = re.sub("<a href=\".*?\" class=\".*?\">{0}</a>".format(Link), Link, info)

		Origins = []
		for h in re.split("<BR><BR>", info):
			if h != "":
				Origins.append(h)
		return Origins


	def Load(self):
		self.Parser.hookCommand('PRIVMSG', "^@etym", self.Etymology)
		self.Parser.loadedPlugins[self.__name__].append(Settings)
		self.Parser.loadedPlugins[self.__name__].append(self.Load)
		self.Parser.loadedPlugins[self.__name__].append(self.Unload)
		self.Parser.loadedPlugins[self.__name__].append(self.Reload)
	
	def Unload(self):
		pass
	def Reload(self):
		pass
