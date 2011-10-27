#!/usr/bin/python2

import requests
import os, re
# http://www.urbandictionary.com/tooltip.php?term= <-- Thank god for this url.

def request(word):
	h = cached(word)
	if h:
		print('* [UrbanDict] => Sending cached word.')
		return "\x02[UrbanDict]\x02 {0}: {1}".format(word, h)
	else:
		url = "http://www.urbandictionary.com/tooltip.php?term="+word.replace(" ","%20")
		try:
			html = requests.get(url).content
		except:
			print("* [UrbanDict] Error => Failed to connect.")
			return "Failed to connect to Urban Dictionary."

		content = re.compile("<div><b>(.*?)<\/b><\/div><div>(.*?)<\/div>")
		escapes = re.compile(r'[\r\n\t]')
		try:
			result = content.match(escapes.sub('', html.replace("<br/>", " ").strip())).groups()[1]
		except: 
			result = None
		if not result or result is None or result == '':
			return "\x02[UrbanDict]\x02 {0} has not yet been defined.".format(word)
		else:
			result = result.replace('&quot;', '"').replace('<b>', '\x02').replace('</b>', '\x02')
			add_cache(word.lower(), result)
			return "\x02[UrbanDict]\x02 {0}: {1}".format(word, result)

def cached(word):
	try:
		with open('./Plugins/UrbanDict_Cache.txt','r') as c:
			cache = c.read().split('\n')
			for line in cache:
				if word.lower() == line.split(" : ")[0]:
					return line.split(" : ")[1]
			else:
				return False
	except:
		return False
				
def add_cache(word, definition=''):
	if os.access('./Plugins/UrbanDict_Cache.txt', 6):
		with open('./Plugins/UrbanDict_Cache.txt','a') as c:
			print('* [UrbanDict] Cache => Adding word {0}'.format(word))
			c.write("{0} : {1}\n".format(word, definition))
	else:
		with open('./Plugins/UrbanDict_Cache.txt','w') as c:
			print('* [UrbanDict] Cache => Creating Cache')
			print('* [UrbanDict] Cache => Adding word {0}'.format(word))
			c.write("{0} : {1}\n".format(word, definition))
