#!/usr/bin/python2
#Youtube Stats/Link Parser

import requests
import json
import decimal

class YT(object):
	def Main(self, link):
		if not link:
			return None
		try:
			vidId = link.split("watch?v=")[1].split(" ")[0]
			jsonLink = "http://gdata.youtube.com/feeds/api/videos/{0}?alt=json".format(str(vidId))
			jsonReply = requests.get(jsonLink)
			if jsonReply.status_code != 200:
				return None
			jsonReply = json.load(jsonReply)
			return self.Parse(jsonReply)
		except:
			return None
			
	def Parse(self, jsonReply):
		TWOPLACES = decimal.Decimal('0.01')
		D = decimal.Decimal
		
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
		'title':title,
		'author':str(jsonReply['entry']['author'][0]['name']['$t']),
		
		'averagerating':D(jsonReply['entry']['gd$rating']['average']).quantize(TWOPLACES),
		'maxrating':int(jsonReply['entry']['gd$rating']['max']),
		'percentrating':perc,
		'totalvotes':totalvotes,
		'likes':likes,
		'dislikes':dislikes,
				
		'duration':int(jsonReply['entry']['media$group']['yt$duration']['seconds']),
		'viewcount':int(jsonReply['entry']['yt$statistics']['viewCount']),
		'favorites':int(jsonReply['entry']['yt$statistics']['favoriteCount']),
		}
		return stats

