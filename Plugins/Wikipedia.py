#!/usr/bin/env python

# Wikipedia article retriever plugin for WhergBot
# 1.0; 01.01.2012; Edza

# Returns the first paragraph of the article, which conviniently is also the first paragraph of the webpage.
# This is done by hooking both @wiki and wikipedia links.

# This is a very simple initial version.

# Jan 11 - Removed Footnotes from text
# Jan 11 - Fixed a bug with missing 'http://' for requests
# Jan 11 - Removed Unicode bug
# Jan 09 - Added truncate function

import requests
import os, re
from htmldecode import convert

def truncate(content, length=300, suffix='...'):
	if len(content) <= length:
		return content
	else:
		x = u' '.join(content[:length+1].split(u' ')[0:-1]) + u"{0}".format(suffix)
		return x

def getArticleByName(articleName):
	Url = "http://en.wikipedia.org/wiki/Special:Search?search={0}".format(articleName.strip().replace(" ","%20"))
	return "{0} - {1}".format(getArticleByUrl(Url), Url)

def getArticleByUrl(articleUrl):
	if not articleUrl.startswith("http://") and not articleUrl.startswith("https://"):
		articleUrl = "https://{0}".format(articleUrl)
	try:
		articleHtml = requests.get(articleUrl).content
	except:
		print("* [Wikipedia] Error => Failed to connect.")
		return "Failed to connect to Wikipedia."
			
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
	except: 
		result = "Failed to retrieve the Wikipedia article."

	return result


def wikiUrl(msg, sock, users, allowed):
	urls = re.findall("(?:https?:\/\/)?en.wikipedia\.org\/wiki\/.*?(?:\s|$)", msg[4])
	for url in urls:
		try:
			sock.say(msg[3], "\x02[Wikipedia]\x02 {0}".format(getArticleByUrl(url)))
		except Exception, e:
			print("* [Wikipedia] Error:\n* [Wikipedia] {0}".format(str(e)))

def wikiName(msg, sock, users, allowed):
	try:
		article = " ".join(msg[4].split()[1:])
		sock.say(msg[3], "\x02[Wikipedia]\x02 {0}".format(getArticleByName(article)))
	except Exception, e:
		print("* [Wikipedia] Error:\n* [Wikipedia] {0}".format(str(e)))

hooks = {
	'(?:https?:\/\/)?en.wikipedia\.org\/wiki\/': [wikiUrl, 5, False],
	'^@wiki': [wikiName, 5, False],
	}

helpstring = """Returns info about a wikipedia page
@wiki <string>: Searches for a wikipedia page"""
