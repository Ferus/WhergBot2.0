#!/usr/bin/env python
#Youtube Stats/Link Parser

import requests
import json
import decimal
import re

from Parser import Locker
Lock = Locker(5)

from .Settings import Settings

def convert(text):
	"""Decode HTML entities in the given text."""
	try:
		if type(text) is unicode:
			uchr = unichr
		else:
			uchr = lambda value: value > 255 and unichr(value) or chr(value)
		def entitydecode(match, uchr=uchr):
			entity = match.group(1)
			if entity.startswith('#x'):
				return uchr(int(entity[2:], 16))
			elif entity.startswith('#'):
				return uchr(int(entity[1:]))
			elif entity in htmlentitydefs.name2codepoint:
				return uchr(htmlentitydefs.name2codepoint[entity])
			else:
				return match.group(0)
		charrefpat = re.compile(r'&(#(\d+|x[\da-fA-F]+)|[\w.:-]+);?')
		text = charrefpat.sub(entitydecode, text)
		return text
	except Exception, e:
		print("* [YouTube] Error: {0}".format(repr(e)))
		return text

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
		except Exception, e:
			print("* [YouTube] Error: {0}".format(repr(e)))
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
		perc = (D(str(jsonReply['entry']['gd$rating']['average'])) / int(jsonReply['entry']['gd$rating']['max'])).quantize(TWOPLACES)

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

		'averagerating':D(str(jsonReply['entry']['gd$rating']['average'])).quantize(TWOPLACES),
		'maxrating':int(jsonReply['entry']['gd$rating']['max']),
		'percentrating':str(perc).replace(".","").lstrip("0"),
		'totalvotes':totalvotes,
		'likes':likes,
		'dislikes':dislikes,

		'duration':duration,
		'viewcount':"{:1,}".format(int(jsonReply['entry']['yt$statistics']['viewCount'])), # Breaks Py2.6
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
			VidAverage = "{:.2}".format(vidInfo['gd$rating']['average']) # Breaks Py2.6
			VidMax = vidInfo['gd$rating']['max']
			VidNumRaters = vidInfo['gd$rating']['numRaters']
			VidViewCounts = vidInfo['yt$statistics']['viewCount']
			VidFavoriteCount = vidInfo['yt$statistics']['favoriteCount']
			VidLink = "https://youtu.be/"+vidInfo['id']['$t'].split(":")[-1]
			VidLikes = vidInfo['yt$rating']['numLikes']
			VidDisLikes = vidInfo['yt$rating']['numDislikes']
			VidLength = self.ConvertTime(int(vidInfo['media$group']['yt$duration']['seconds']))

			# <Title + Uploader> [Length] <Link> [Average/Max Likes/Dislikes] <Views>
			info = "\x02[YouTube]\x02 Title: \x02{0}\x02".format(VidTitle) if VidTitle else ""
			info += "- By: \x02{0}\x02".format(Uploader) if Uploader else ""
			info += " [Length: \x02{0}\x02]".format(VidLength) if VidLength else ""
			info += " <Link: {0}>".format(VidLink) if VidLink else ""
			info += " [Rating: \x02{0}\x02/\x02{1}\x02]".format(VidAverage, VidMax) if VidAverage and VidMax else ""
			info += " <(Dis)Likes: \x02{0}\x02/\x02{1}\x02>".format(VidLikes, VidDisLikes) if VidLikes and VidDisLikes else ""
			info += " [Views: \x02{0}\x02]".format(VidViewCounts) if VidViewCounts else ""
			results.append(info)
		return results


class Main(YT):
	def __init__(self, Name, Parser):
		self.__name__ = Name
		self.Parser = Parser
		self.IRC = self.Parser.IRC
	
	def YouTubeStats(self, data):
		vidIds = list(set(re.findall("v=([a-zA-Z0-9_\-]{11})", ' '.join(data[3:]) )))
		for vidId in vidIds:
			x = self.Main(vidId)
			if x != None:
				info = "\x02[YouTube]\x02 {0}".format(x['title'] if x['title'] else '')
				info += " - By: \x02{0}\x02".format(x['author']) if x['author'] else ''
				info += " [\x02{0}\x02]".format(x['duration']) if x['duration'] else ''
				info += " \x02{0}\x02/\x02{1}\x02 (\x02{2}%\x02)".format(x['averagerating'], x['maxrating'], x['percentrating']) \
					if x['averagerating'] and x['maxrating'] and x['percentrating'] else ''
	
				info += " \x02{0}\x02 Views".format(x['viewcount']) if x['viewcount'] else ''
				info += " \x02{0}\x02 Likes".format(x['likes']) if x['likes'] else ''
				info += " \x02{0}\x02 Dislikes".format(x['dislikes']) if x['dislikes'] else ''
				info += " \x02{0}\x02 Total".format(x['totalvotes']) if x['totalvotes'] else ''
				self.IRC.say(data[2], info)
			else:
				pass
	
	def YouTubeGetVids(self, data):
		if Lock.Locked:
			self.IRC.notice(data[0].split('!')[0], "Please wait a few seconds before using this command again.")
			return None
		try:
			terms = "+".join(data[4:]).replace("|","%7C")
		except:
			self.IRC.say(data[2], "Supply some searchterms you derp!")
		for vid in self.Search(terms, results=3):
			self.IRC.say(data[2], vid)
		Lock.Lock()

	def Load(self):
		self.Parser.hookCommand("PRIVMSG", "(?:https?:\/\/)?(?:www\.)?youtube\.com\/.*?", self.YouTubeStats)
		self.Parser.hookCommand("PRIVMSG", "^@yt .*?$", self.YouTubeGetVids)
		self.Parser.loadedPlugins[self.__name__].append(Settings)
		self.Parser.loadedPlugins[self.__name__].append(self.Load)
		self.Parser.loadedPlugins[self.__name__].append(self.Unload)
		self.Parser.loadedPlugins[self.__name__].append(self.Reload)

	
	def Unload(self):
		pass
	def Reload(self):
		pass

