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
			vidId = re.findall("\?v=[a-zA-Z0-9_\Q-\E]{11}", link)[0][3:]
			jsonLink = "http://gdata.youtube.com/feeds/api/videos/{0}?alt=json".format(vidId)
			jsonReply = requests.get(jsonLink)
			if jsonReply.status_code != 200:
				return None
			jsonReply = json.load(jsonReply) # .load() requires an object that can .read()
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

