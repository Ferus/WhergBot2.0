#!/usr/bin/env python

# Wikipedia article retriever plugin for WhergBot
# 1.0; 01.01.2012; Edza

# Returns the first paragraph of the article, which conviniently is also the first paragraph of the webpage.
# This is done by hooking both @wiki and wikipedia links.

# This is a very simple initial version.

# Jun 15 - Ported to new Wherg
# Feb 29 - Use requests.url when returning text from getArticleByUrl
# Feb 06 - Added a Command Locker
# Jan 11 - Removed Footnotes from text
# Jan 11 - Fixed a bug with missing 'http://' for requests
# Jan 11 - Removed Unicode bug
# Jan 09 - Added truncate function

import requests
import os, re

from .Settings import Settings
from Parser import Locker
Locker = Locker(5)

def truncate(content, length=300, suffix='...'):
	if len(content) <= length:
		return content
	else:
		x = ' '.join(content[:length+1].split(' ')[0:-1]) + "{0}".format(suffix)
		return x

def getArticleByName(articleName):
	Url = "http://en.wikipedia.org/wiki/Special:Search?search={0}".format(articleName.strip().replace(" ","%20"))
	return getArticleByUrl(Url, returnUrl=True)

def getArticleByUrl(articleUrl, returnUrl=False):
	if not articleUrl.startswith("http://") and not articleUrl.startswith("https://"):
		articleUrl = "http://" + articleUrl

	try:
		articleReq = requests.get(articleUrl)
		articleReq.raise_for_status()
		articleHtml = articleReq.text
	except (requests.HTTPError, requests.ConnectionError) as e:
		print("* [Wikipedia] Error => {0}".format(repr(e)))
		return repr(e)
	except Exception as e:
		print("* [Wikipedia] Error => {0}".format(repr(e)))
		return repr(e)

	titleRegex = re.compile("<title>(.*?) -")
	firstParaRegex = re.compile("<p>(.*?)[\r\n]?<\/p>")
	footnoteRegex = re.compile("\[[0-9]{1,3}\]")

	# Special cases
	disambRegex = re.compile('may refer to:$')
	notfoundRegex = re.compile('Other reasons this message may be displayed:')

	try:
		title = re.sub('<[^<]+?>', '', titleRegex.search(articleHtml).group())
		text = re.sub('<[^<]+?>', '', firstParaRegex.search(articleHtml).group())
		text = footnoteRegex.sub('', text)

		text = truncate(text)

		if disambRegex.search(text):
			text = "Disambiguations are not yet supported."
		elif notfoundRegex.search(text):
			text = "Article not found."

		result = "{0} {1}".format(title, text)

		if returnUrl:
			result += " - {0}".format(articleReq.url)
	except Exception as e:
		result = "Failed to retrieve the Wikipedia article."

	return result

class Main(object):
	def __init__(self, Name, Parser):
		self.__name__ = Name
		self.Parser = Parser
		self.IRC = self.Parser.IRC

	def wikiUrl(self, data):
		urls = re.findall("(?:https?:\/\/)?en.wikipedia\.org\/wiki\/.*?(?:\s|$)", ' '.join(data[3:]))
		for url in urls:
			try:
				self.IRC.say(data[2], "\x02[Wikipedia]\x02 {0}".format(getArticleByUrl(url)))
			except Exception as e:
				print("* [Wikipedia] Error:\n* [Wikipedia] {0}".format(str(e)))

	def wikiName(self, data):
		try:
			if not Locker.Locked:
				article = " ".join(data[4:])
				self.IRC.say(data[2], "\x02[Wikipedia]\x02 {0}".format(getArticleByName(article)))
				Locker.Lock()
			else:
				self.IRC.notice(data[0].split('!')[0], "Please wait a little longer before using this command again.")
		except Exception as e:
			print("* [Wikipedia] Error:\n* [Wikipedia] {0}".format(str(e)))

	def Load(self):
		self.Parser.hookCommand("PRIVMSG", "^@wiki .*?$", self.wikiName)
		self.Parser.hookCommand("PRIVMSG", "(?:https?:\/\/)?en.wikipedia\.org\/wiki\/.*?", self.wikiUrl)
		self.Parser.hookPlugin(self.__name__, Settings, self.Load, self.Unload, self.Reload)

	def Unload(self):
		pass
	def Reload(self):
		pass
