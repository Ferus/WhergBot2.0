#!/usr/bin/python2
#Youtube Stats/Link Parser

import requests
import json
import decimal
import re

from htmldecode import convert

class YT(object):
	def Main(self, vidId):
		if not vidId:
			return None
		try:
			jsonLink = "http://gdata.youtube.com/feeds/api/videos/{0}?alt=json".format(vidId)
			jsonReply = requests.get(jsonLink)
			if jsonReply.status_code != 200:
				return None
			jsonReply = json.loads(jsonReply.content)
			return self.Parse(jsonReply)
		except:
			return None

	def ConvertTime(self, seconds):
		minutes, seconds = divmod(seconds, 60)
		hours, minutes = divmod(minutes, 60)
		duration = ""
		if hours != 0:
			duration += "{0}:".format(str(hours).zfill(2))
		duration += "{0}:{1}".format(str(minutes).zfill(2), str(seconds).zfill(2))
		return duration
			
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
			
		title = jsonReply['entry']['title']['$t'].encode('utf-8')
		duration = self.ConvertTime(int(jsonReply['entry']['media$group']['yt$duration']['seconds']))

		stats = {
		'title':convert(title),
		'author':convert(str(jsonReply['entry']['author'][0]['name']['$t'])),
		
		'averagerating':D(jsonReply['entry']['gd$rating']['average']).quantize(TWOPLACES),
		'maxrating':int(jsonReply['entry']['gd$rating']['max']),	
		'percentrating':str(perc).replace(".","").lstrip("0"),
		'totalvotes':totalvotes,
		'likes':likes,
		'dislikes':dislikes,
		
		'duration':duration,
		'viewcount':"{:1,}".format(int(jsonReply['entry']['yt$statistics']['viewCount'])),
		'favorites':int(jsonReply['entry']['yt$statistics']['favoriteCount']),
		}
		return stats

	def Search(self, terms, results=2):
		link = "https://gdata.youtube.com/feeds/api/videos?q={0}&safeSearch=none&max-results={1}&v=2&alt=json".format(terms, results)
		try:
			req = requests.get(link)
			if req.status_code != 200:
				return None #Error'd Wat.
			jsonReply = json.loads(req.content)['feed']['entry']
		except Exception, e:
			print("* [YouTube] Error:\n* [YouTube] {0}".format(repr(e)))
			return ['\x02[YouTube]\x02 Failed to get info.']

		results = []
		for vidInfo in jsonReply:
			Uploader = vidInfo['author'][0]['name']['$t']
			VidTitle = vidInfo['title']['$t']
			VidAverage = "{:.2}".format(vidInfo['gd$rating']['average'])
			VidMax = vidInfo['gd$rating']['max']
			VidNumRaters = vidInfo['gd$rating']['numRaters']
			VidViewCounts = vidInfo['yt$statistics']['viewCount']
			VidFavoriteCount = vidInfo['yt$statistics']['favoriteCount']
			VidLink = "https://youtu.be/"+vidInfo['id']['$t'].split(":")[-1]
			VidLikes = vidInfo['yt$rating']['numLikes']
			VidDisLikes = vidInfo['yt$rating']['numDislikes']
			VidLength = vidInfo['media$group']['yt$duration']['seconds']
			VidLength = self.ConvertTime(int(VidLength))
			
			# <Title + Uploader> [Length] <Link> [Average/Max Likes/Dislikes] <Views>
			info = "\x02[YouTube]\x02 Title: \x02{0}\x02 - By: \x02{1}\x02".format(VidTitle, Uploader)
			info += " [Length: \x02{0}\x02] <Link: {1}>".format(VidLength, VidLink)
			info += " [Rating: \x02{0}\x02/\x02{1}\x02]".format(VidAverage, VidMax)
			info += " <(Dis)Likes: \x02{0}\x02/\x02{1}\x02>".format(VidLikes, VidDisLikes)
			info += " [Views: \x02{0}\x02]".format(VidViewCounts)
			results.append(info)
		return results

YouTube = YT()

def youtubestats(msg, sock, users, allowed):
	vidId = re.findall("=[a-zA-Z0-9_\-]{11}", msg[4])[0][1:]
	x = YouTube.Main(vidId)
	if x != None:
	# [YouTube] title - By: author {duration} <averagerating/maxrating (percentrating%)> [x Likes/x Dislikes/x Total]
		head = "\x02[YouTube]\x02 {0} - By: \x02{1}\x02 [\x02{2}\x02]".format(x['title'], x['author'], x['duration'])
		middle = "<\x02{0}\x02/\x02{1}\x02 (\x02{2}%\x02) \x02{3}\x02 Views>".format(x['averagerating'], x['maxrating'], x['percentrating'], x['viewcount'])
		tail = "[\x02{0}\x02 Likes/\x02{1}\x02 Dislikes/\x02{2}\x02 Total]".format(x['likes'], x['dislikes'], x['totalvotes'])
		
		y = "{0} {1} {2}".format(head, middle, tail)
		sock.say(msg[3], y)
	else:
		pass

def YouTubeGetVids(msg, sock, users, allowed):
	try:
		terms = "+".join(msg[4].split()[1:]).replace("|","%7C")
	except:
		sock.say(msg[3], "Supply some searchterms you derp!")
	for vid in YouTube.Search(terms, results=1):
		sock.say(msg[3], vid)
		
hooks = {
	'(?:https?:\/\/)?(?:www\.)?youtube\.com\/': [youtubestats, 5, False],
	'^@yt': [YouTubeGetVids, 5, False],
		}
