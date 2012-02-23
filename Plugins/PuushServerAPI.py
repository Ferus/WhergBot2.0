#!/usr/bin/env python
import requests
import json
import re

'''
https://github.com/KevinLi/PuushServer
Uses API link to get data
'''

#http://199.19.116.75:1234/api?file=xxxx
#http://b.pyboard.net:1234/api?file=xxxx
_REGEX = '199.19.116.75|b.pyboard.net\:[0-9]{4,5}/api\?file=[a-zA-Z0-9]{4}'

def Get(id):
	req = requests.get("http://199.19.116.75:1234/api?file={0}".format(id))
	if not req.status_code == 200:
		return None
	data = json.loads(req.content)
	return data

def Format(data):
	s = ""
	s += "\x02[Puush]\x02"
	s += " File \x02{0}\x02".format(data['filename'])
	s += " (\x02{0}\x02)".format(data['mimetype'])
	s += " [\x02{0}\x02]".format(data['timestamp'])
	s += " Views: \x02{0}\x02".format(data['views'])
	return s

def Main(msg, sock, users, allowed):
	links = []
	for x in re.findall(_REGEX, msg[4]):
		links.append(x.split('file=')[1])

	for x in links:
		data = Get(x)
		if not data:
			pass
		else:
			sock.say(msg[3], Format(data))

hooks = {
	_REGEX: [Main, 5, False],
		}

helpstring = "Sorta like Imgur.py but for https://github.com/KevinLi/PuushServer"
