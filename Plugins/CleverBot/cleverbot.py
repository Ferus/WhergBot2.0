#!/usr/bin/python
"""
Ha ha ha, stolen codes!
Found this on pastebin and modified it.


This library lets you open chat session with cleverbot (www.cleverbot.com)
Example of how to use the bindings:
>>> import cleverbot
>>> cb=cleverbot.Session()
>>> print cb.Ask("Hello there")
'Hello.'
"""

import requests
import hashlib
import re
class ServerFullError(Exception):
	pass

ReplyFlagsRE = re.compile('<INPUT NAME=(.+?) TYPE=(.+?) VALUE="(.*?)">', re.IGNORECASE | re.MULTILINE)

class Session(object):
	def __init__(self):
		self.arglist = ['', 'y', '', '', '', '', '', '', '','', 'wsf',
			'', '', '', '', '', '', '', '', '0', 'Say', '1', 'false']
		self.MsgList = []
		self.keylist = ['stimulus'
			,'start'
			,'sessionid'
			,'vText8'
			,'vText7'
			,'vText6'
			,'vText5'
			,'vText4'
			,'vText3'
			,'vText2'
			,'icognoid'
			,'icognocheck'
			,'prevref'
			,'emotionaloutput'
			,'emotionalhistory'
			,'asbotname'
			,'ttsvoice'
			,'typing'
			,'lineref'
			,'fno'
			,'sub'
			,'islearning'
			,'cleanslate'
			]
		self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:7.0.1) Gecko/20100101 Firefox/7.0'
			,'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
			,'Accept-Language': 'en-us;q=0.8,en;q=0.5'
			,'X-Moz': 'prefetch'
			,'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7'
			,'Referer': 'http://www.cleverbot.com'
			,'Cache-Control': 'no-cache, no-cache'
			,'Pragma': 'no-cache'
			}


	def Send(self):
		data = Encode(self.keylist, self.arglist)
		digest_txt = data[9:29]
		h = hashlib.md5(digest_txt.encode('utf-8')).hexdigest()
		self.arglist[self.keylist.index('icognocheck')] = h
		data = Encode(self.keylist, self.arglist)
		req = requests.post("http://www.cleverbot.com/webservicemin", data=data, headers=self.headers)
		reply = req.text
		return reply

	def Ask(self, q):
		self.arglist[self.keylist.index('stimulus')] = q
		if self.MsgList:
			self.arglist[self.keylist.index('lineref')] = '!0'+str(len(self.MsgList)/2)
		reply = self.Send()
		self.MsgList.append(q)
		reply = ParseAnswer(reply)
		for k, v in reply.items():
			try:
				self.arglist[self.keylist.index(k)] = v
			except ValueError:
				pass
		self.arglist[self.keylist.index('emotionaloutput')] = ''
		text = reply['ttsText']
		self.MsgList.append(text)
		return text

def ParseAnswer(text):
	d = {}
	keys = ["text", "sessionid", "logurl", "vText8", "vText7", "vText6", "vText5", "vText4", "vText3",
		"vText2", "prevref", "foo", "emotionalhistory", "ttsLocMP3", "ttsLocTXT",
		"ttsLocTXT3", "ttsText", "lineRef", "lineURL", "linePOST", "lineChoices",
		"lineChoicesAbbrev", "typingData", "divert"]
	values = text.split("\r")
	i = 0
	for key in keys:
		d[key] = values[i]
		i += 1
	return d

def Encode(keylist, arglist):
	text = ''
	for i in range(len(keylist)):
		k = keylist[i]
		v = quote(arglist[i])
		text += '&' + k + '=' + v
	text = text[1:]
	return text

always_safe = ('ABCDEFGHIJKLMNOPQRSTUVWXYZ'
	'abcdefghijklmnopqrstuvwxyz'
	'0123456789' '_.-')

def quote(s, safe = '/'):
	#quote('abc def') -> 'abc%20def'
	safe += always_safe
	safe_map = {}
	for i in range(256):
		c = chr(i)
		safe_map[c] = (c in safe) and c or ('%%%02X' % i)
	res = list(map(safe_map.__getitem__, s))
	return ''.join(res)


def main():
	import sys
	cb = Session()
	q = ''
	while q != 'bye':
		try:
			q = input("> ")
		except KeyboardInterrupt:
			print()
			sys.exit()
		print(cb.Ask(q))

def two():
	cb1 = Session()
	cb2 = Session()
	r1 = cb1.Ask("Hello there, I am Cleverbot!")
	print("CleverBot 1-> "+r1)
	while True:
		try:
			r2 = cb2.Ask(r1)
			print("CleverBot 2-> "+r2)
			r1 = cb1.Ask(r2)
			print("CleverBot 1-> "+r1)
		except KeyboardInterrupt:
			break

if __name__ == "__main__":
	two()



