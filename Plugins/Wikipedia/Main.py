#!/usr/bin/env python

# Wikipedia article retriever plugin for WhergBot
# 1.0; 01.01.2012; Edza

# Returns the first paragraph of the article, which conviniently is also the first paragraph of the webpage.
# This is done by hooking both @wiki and wikipedia links.

# This is a very simple initial version.

# Oct 06 - Finished™ porting to Wikipedia's API.
# Oct 04 - Attempt at changing over to Wikipedia's API/Cacheing articles.
# Jun 15 - Ported to new Wherg
# Feb 29 - Use requests.url when returning text from getArticleByUrl
# Feb 06 - Added a Command Locker
# Jan 11 - Removed Footnotes from text
# Jan 11 - Fixed a bug with missing 'http://' for requests
# Jan 11 - Removed Unicode bug
# Jan 09 - Added truncate function

import re
from . import Wikipedia
from .Settings import Settings
from Parser import Locker
Locker = Locker(5)

class Main(object):
	def __init__(self, Name, Parser):
		self.__name__ = Name
		self.Parser = Parser
		self.IRC = self.Parser.IRC
		self.Wiki = Wikipedia.WikipediaAPIWrapper(Database = "Plugins/Wikipedia/Wiki.db")

	def wikiUrl(self, data):
		urls = re.findall("(?:https?:\/\/)?en.wikipedia\.org\/wiki\/.*?(?:\s|$)", ' '.join(data[3:]))
		for url in urls:
			article = url.split('/')[-1]
			section = ''
			if "#" in article:
				article, section = article.split("#")
			article = self.Wiki.searchWikipediaForArticles(article)
			try:
				article = self.Wiki.getArticleFromDatabase(article)
			except Wikipedia.ArticleNotInDatabase:
				article = self.Wiki.getArticleFromWikipedia(article)
			article = article[0]
			if section != '':
				article = Wikipedia.truncate(article[section])
			else:
				article = Wikipedia.truncate(article['description'])
			self.IRC.say(data[2], "\x02[Wikipedia]\x02 {0}".format(article))

	def wikiName(self, data):
		if Locker.Locked:
			self.IRC.notice(data[0].split("!")[0], "Please wait a little longer before using this command again.")
			return None
		article = self.Wiki.searchWikipediaForArticles(" ".join(data[4:]))
		try:
			article = self.Wiki.getArticleFromDatabase(article)
		except Wikipedia.ArticleNotInDatabase:
			article = self.Wiki.getArticleFromWikipedia(article)
		article = article[0]
		article = Wikipedia.truncate(article['description'])
		self.IRC.say(data[2], "\x02[Wikipedia]\x02 {0}".format(article))
		Locker.Lock()

	def Load(self):
		self.Parser.hookCommand("PRIVMSG", "^@wiki .*?$", self.wikiName)
		self.Parser.hookCommand("PRIVMSG", "(?:https?:\/\/)?en.wikipedia\.org\/wiki\/(?!File:)[\w%]+", self.wikiUrl)
		self.Parser.hookPlugin(self.__name__, Settings, self.Load, self.Unload, self.Reload)

	def Unload(self):
		pass
	def Reload(self):
		pass
