#!/usr/bin/env python

import requests
import os, re
import json

from htmldecode import convert
from CommandLock import Locker
Locker = Locker(5)
# http://www.urbandictionary.com/tooltip.php?term= <-- Thank god for this url.

def UDrequest(msg, sock, users, allowed):
	try:
		if Locker.Locked:
			sock.notice(msg[0], "Please wait a little bit longer before using this command")
			return None
		word = " ".join(msg[4].split()[1:])
		if not word:
			sock.notice(msg[0], "Derp!")
			return None
	except Exception, e:
		print("* [UrbanDict] Error: line 22\n* [UrbanDict] {0}".format(str(e)))

	h = cached(word)
	if h:
		print('* [UrbanDict] => Sending cached word.')
		sock.say(msg[3], "\x02[UrbanDict]\x02 {0}: {1}".format(word, h))
		Locker.Lock()
		return None
	else:
		print("* [UrbanDict] => Polling UrbanDictionary.")
		url = "http://www.urbandictionary.com/tooltip.php?term="+str(word).replace(" ","%20")
		try:
			html = requests.get(url).content
		except requests.HTTPError:
			print("* [UrbanDict] Error => Failed to connect.")
			sock.say(msg[3], "Failed to connect to Urban Dictionary.")
			return None

		html = html.replace("\\u003C", "<").replace("\\u003E",">")
		html = json.loads(html)['string']

		try:
			result = re.sub(r'[\r\n\t]', "", html)
			result, other = re.search("<div>\s*<b>.*?</b></div><div>\s*(?:.*?<br/><br/>)?(.*?)</div>(?:<div class='others'>\s*(.*?)</div>)?", result).groups()
		except Exception, e:
			print("* [UrbanDict] Error: line 47\n* [UrbanDict] {0}".format(repr(e)))
			result = None
		if not result or result is None or result == '':
			sock.say(msg[3], "\x02[UrbanDict]\x02 {0} has not yet been defined.".format(word))
			return None

		results = []
		for x in re.split("<br/>", result):
			if x == " " or x == "":
				pass
			x = x.replace('&quot;', '"').replace('<b>', '\x02').replace('</b>', '\x02').replace('<br/>', '')
			results.append(x)
		add_cache(word.lower(), " ".join(results))

		for y in results:
			sock.say(msg[3], "\x02[UrbanDict]\x02 {0}: {1}".format(word, y))
		Locker.Lock()

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

hooks = {
	'^@ud': [UDrequest, 5, False],
		}

helpstring = "@ud <Word>: Polls UrbanDictionary for a word if that word is not already in the local cache"
