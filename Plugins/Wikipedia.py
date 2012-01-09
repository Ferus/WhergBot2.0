# Wikipedia article retriever plugin for WhergBot
# 1.0; 01.01.2012; Edza

# Returns the first paragraph of the article, which conviniently is also the first paragraph of the webpage.
# This is done by hooking both @wiki and wikipedia links.

# This is a very simple initial version.

import requests
import os, re
from htmldecode import convert

def getArticleByName(articleName):
	return getArticleByUrl("http://en.wikipedia.org/wiki/"+articleName.strip().replace(" ","%20"));

def getArticleByUrl(articleUrl):
	try:
		articleHtml = requests.get(articleUrl).content.encode("utf-8")
	except:
		print("* [Wikipedia] Error => Failed to connect.");
		return "Failed to connect to Wikipedia."
			
	titleRegex = re.compile("<title>(.*?) -");
	firstParaRegex = re.compile("<p>(.*?)[\r\n]?<\/p>");
	
	# Special cases
	disambRegex = re.compile('may refer to:$')
	notfoundRegex = re.compile('Other reasons this message may be displayed:');
	
	try:
		title = re.sub('<[^<]+?>', '', titleRegex.search(articleHtml).group());
		text = re.sub('<[^<]+?>', '', firstParaRegex.search(articleHtml).group());

		if disambRegex.search(text):
			text = "Disambiguations are not yet supported."
		elif notfoundRegex.search(text):
			text = "Article not found."
					
		result = "{0} {1} - {2}".format(title, text, articleUrl)
	except: 
		result = "Failed to retrieve the Wikipedia article.";
	return result;

def wikiUrl(msg, sock, users, allowed):
	try:
		sock.say(msg[3], u"\x02[Wikipedia]\x02 {0}".format(getArticleByUrl(msg[4])))
	except Exception, e:
		print("* [Wikipedia] Error:\n* [Wikipedia] {0}".format(str(e)))

def wikiName(msg, sock, users, allowed):
	try:
		sock.say(msg[3], u"\x02[Wikipedia]\x02 {0}".format(getArticleByName(" ".join(msg[4].split()[1:]))))
	except Exception, e:
		print("* [Wikipedia] Error:\n* [Wikipedia] {0}".format(str(e)))

hooks = {
	'(?:https?:\/\/)?en.wikipedia\.org\/wiki\/': [wikiUrl, 5, False],
	'^@wiki': [wikiName, 5, False],
	}
