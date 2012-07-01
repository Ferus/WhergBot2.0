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

def convert(text):
	"""Decode HTML entities in the given text."""
	try:
		if type(text) is unicode:
			uchr = unichr
		else:
			uchr = lambda value: value > 255 and unichr(value) or chr(value)
		def entitydecode(match, uchr=uchr):
			entity = match.group(1)
			if entity.startswith('#x'):
				return uchr(int(entity[2:], 16))
			elif entity.startswith('#'):
				return uchr(int(entity[1:]))
			elif entity in htmlentitydefs.name2codepoint:
				return uchr(htmlentitydefs.name2codepoint[entity])
			else:
				return match.group(0)
		charrefpat = re.compile(r'&(#(\d+|x[\da-fA-F]+)|[\w.:-]+);?')
		text = charrefpat.sub(entitydecode, text)
		return text
	except Exception, e:
		print("* [UrbanDict] Error: {0}".format(repr(e)))
		return text

def truncate(content, length=300, suffix='...'):
	if len(content) <= length:
		return content
	else:
		x = u' '.join(content[:length+1].split(u' ')[0:-1]) + u"{0}".format(suffix)
		return x

def getArticleByName(articleName):
	Url = "http://en.wikipedia.org/wiki/Special:Search?search={0}".format(articleName.strip().replace(" ","%20"))
	return "{0}".format(getArticleByUrl(Url, returnUrl=True))

def getArticleByUrl(articleUrl, returnUrl=False):
	if not articleUrl.startswith("http://") and not articleUrl.startswith("https://"):
		articleUrl = "https://{0}".format(articleUrl)
	try:
		articleReq = requests.get(articleUrl)
		if articleReq.status_code != 200:
			raise requests.HTTPError
		articleHtml = articleReq.content
	except requests.HTTPError, e:
		print("* [Wikipedia] Error => {0}".format(repr(e)))
		return repr(e)
	except Exception, e:
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

		text = truncate(text).encode("utf-8")

		if disambRegex.search(text):
			text = "Disambiguations are not yet supported."
		elif notfoundRegex.search(text):
			text = "Article not found."

		result = "{0} {1}".format(title, text)

		if returnUrl:
			result += " - {0}".format(articleReq.url)
	except:
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
			except Exception, e:
				print("* [Wikipedia] Error:\n* [Wikipedia] {0}".format(str(e)))
	
	def wikiName(self, data):
		try:
			if not Locker.Locked:
				article = " ".join(data[4:])
				self.IRC.say(data[2], "\x02[Wikipedia]\x02 {0}".format(getArticleByName(article)))
				Locker.Lock()
			else:
				self.IRC.notice(data[0].split('!')[0], "Please wait a little longer before using this command again.")
		except Exception, e:
			print("* [Wikipedia] Error:\n* [Wikipedia] {0}".format(str(e)))

	def Load(self):
		self.Parser.hookCommand("PRIVMSG", "^@wiki .*?$", self.wikiName)
		self.Parser.hookCommand("PRIVMSG", "(?:https?:\/\/)?en.wikipedia\.org\/wiki\/.*?", self.wikiUrl)
		self.Parser.loadedPlugins[self.__name__].append(Settings)
		self.Parser.loadedPlugins[self.__name__].append(self.Load)
		self.Parser.loadedPlugins[self.__name__].append(self.Unload)
		self.Parser.loadedPlugins[self.__name__].append(self.Reload)

	def Unload(self):
		pass
	def Reload(self):
		pass
