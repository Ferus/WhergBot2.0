#!/usr/bin/python2
#Youtube Stats/Link Parser

import requests
import json
import decimal
import re

from htmldecode import convert

class YT(object):
	def Main(self, link):
		if not link:
			return None
		try:
			vidId = re.findall("v=[a-zA-Z0-9_\-]{11}", link)[0][2:]
			jsonLink = "http://gdata.youtube.com/feeds/api/videos/{0}?alt=json".format(vidId)
			jsonReply = requests.get(jsonLink)
			if jsonReply.status_code != 200:
				return None
			jsonReply = json.loads(jsonReply.content)
			return self.Parse(jsonReply)
		except:
			return None
			
	def Parse(self, jsonReply):
		D = decimal.Decimal
		TWOPLACES = D('0.01')
		
		totalvotes = int(jsonReply['entry']['gd$rating']['numRaters'])
		perc = (D(jsonReply['entry']['gd$rating']['average']) / int(jsonReply['entry']['gd$rating']['max'])).quantize(TWOPLACES)

		try:
			likes = int(jsonReply['entry']['yt$rating']['numLikes'])
			dislikes = int(jsonReply['entry']['yt$rating']['numDislikes'])
		except:
			likes = int(totalvotes*float(perc))
			dislikes = int(totalvotes-likes)
			
		title = jsonReply['entry']['title']['$t']
		if type(title) != str:
			title = title.encode('utf-8')

		stats = {
		'title':convert(title),
		'author':convert(str(jsonReply['entry']['author'][0]['name']['$t'])),
		
		'averagerating':D(jsonReply['entry']['gd$rating']['average']).quantize(TWOPLACES),
		'maxrating':int(jsonReply['entry']['gd$rating']['max']),
		'percentrating':perc,
		'totalvotes':totalvotes,
		'likes':likes,
		'dislikes':dislikes,
		
		'duration':int(jsonReply['entry']['media$group']['yt$duration']['seconds']),
		'viewcount':"{:1,}".format(int(jsonReply['entry']['yt$statistics']['viewCount'])),
		'favorites':int(jsonReply['entry']['yt$statistics']['favoriteCount']),
		}
		return stats

YouTube = YT()

def youtubestats(msg, sock, users, allowed):
	link = "http"+msg[4].split("http")[1].split(" ")[0]
	x = YouTube.Main(link)
	if x != None:
	# [YouTube] title - By: author {duration} <averagerating/maxrating (percentrating%)> [x Likes/x Dislikes/x Total]
		head = "\x02[YouTube]\x02 {0} - By: \x02{1}\x02 [\x02{2}\x02 seconds]".format(x['title'], x['author'], str(x['duration']))
		middle = "<\x02{0}\x02/\x02{1}\x02 (\x02{2}%\x02) \x02{3}\x02 Views>".format(str(int(x['averagerating'])), str(x['maxrating']), str(x['percentrating'])[2:], str(x['viewcount']))
		tail = "[\x02{0}\x02 Likes/\x02{1}\x02 Dislikes/\x02{2}\x02 Total]".format(str(x['likes']), str(x['dislikes']), str(x['totalvotes']))
		
		y = "{0} {1} {2}".format(head, middle, tail)
		sock.say(msg[3], y)
	else:
		pass
		
hooks = {
	'http:\/\/(?:www\.)?youtube\.com\/watch': [youtubestats, 5, False],	
		}

