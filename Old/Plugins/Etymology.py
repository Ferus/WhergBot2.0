#!/usr/bin/env python

import re
import requests
from CommandLock import Locker

"""
Etymology.py - Word Origins
"""

Locker = Locker(5)

def Etymology(Message, Socket, Users, Allowed):
	try:
		if Locker.Locked:
			sock.notice(Message[0], "Please wait a little bit longer before using this command")
			return None
		word = " ".join(Message[4].split()[1:])
		if not word:
			sock.notice(Message[0], "Derp!")
			return None
	except Exception, e:
		print("* [Etymology] Error: line 23\n* [Etymology] {0}".format(str(e)))

	Origins = getWordEtymology(word)
	for h in Origins:
		Socket.say(Message[3], "\x02[Etymology]\x02 {0} - {1}".format(word, h))

def getWordEtymology(word):
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

hooks = {
	"^@etym": [Etymology, 5, False]
}

if __name__ == '__main__':
	import sys
	for x in getWordEtymology(sys.argv[-1]):
		print("{0} - {1}\n".format(sys.argv[-1], x.replace("\x02","")))
