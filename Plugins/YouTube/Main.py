#!/usr/bin/env python
#Youtube Stats/Link Parser

import requests
import json
import re

from Parser import Locker
Lock = Locker(5)

class YT(object):
	def Main(self, vidId):
		if not vidId:
			return None
		r = requests.get("http://gdata.youtube.com/feeds/api/videos/{0}?alt=json&v=2".format(vidId))
		try:
			r.raise_for_status()
		except (requests.HTTPError, requests.ConnectionError):
			return None
		r = json.loads(r.text)
		return self.Parse(r)

	def ConvertTime(self, seconds):
		minutes, seconds = divmod(seconds, 60)
		hours, minutes = divmod(minutes, 60)
		duration = ""
		if hours != 0:
			duration += "{0}:".format(str(hours).zfill(2))
		duration += "{0}:{1}".format(str(minutes).zfill(2), str(seconds).zfill(2))
		return duration

	def Parse(self, reply):
		return {'title': reply['entry']['title']['$t']
			,'duration': self.ConvertTime(int(reply['entry']['media$group']['yt$duration']['seconds']))
			,'author': reply['entry']['author'][0]['name']['$t']
			,'averagerating': str(reply['entry']['gd$rating']['average'])[:4]
			,'maxrating': reply['entry']['gd$rating']['max']
			,'numLikes': reply['entry']['yt$rating']['numLikes']
			,'numDislikes': reply['entry']['yt$rating']['numDislikes']
			,'viewCount': reply['entry']['yt$statistics']['viewCount']}

	def Search(self, terms, results=2):
		link = "https://gdata.youtube.com/feeds/api/videos?q={0}&safeSearch=none&max-results={1}&v=2&alt=json".format(terms, results)
		try:
			r = requests.get(link)
			if r.status_code != 200:
				return None #Error'd Wat.
			r = json.loads(r.text)['feed']['entry']
		except Exception as e:
			print("* [YouTube] Error:\n* [YouTube] {0}".format(repr(e)))
			return ['\x02[YouTube]\x02 Failed to get info.']

		results = []
		for vidInfo in r:
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
			info = "\x02[YouTube]\x02 Title: \x02{0}\x02".format(VidTitle)
			info += "- By: \x02{0}\x02".format(Uploader)
			info += " [Length: \x02{0}\x02]".format(VidLength)
			info += " <Link: {0}>".format(VidLink)
			info += " [Rating: \x02{0}\x02/\x02{1}\x02]".format(VidAverage, VidMax)
			info += " <Likes/Dislikes: \x02{0}\x02/\x02{1}\x02>".format(VidLikes, VidDisLikes)
			info += " [Views: \x02{0}\x02]".format(VidViewCounts)
			results.append(info)
		return results


class Main(YT):
	def __init__(self, Name, Parser):
		self.__name__ = Name
		self.Parser = Parser
		self.IRC = self.Parser.IRC
		YT.__init__(self)

	def YouTubeStats(self, data):
		vidIds = list(set(re.findall("v=([a-zA-Z0-9_\-]{11})", ' '.join(data[3:]) )))
		for vidId in vidIds:
			x = self.Main(vidId)
			if x != None:
				info = "\x02[YouTube]\x02 {0}".format(x['title'])
				info += " - By: \x02{0}\x02".format(x['author'])
				info += " [\x02{0}\x02]".format(x['duration'])
				info += " - \x02{0}\x02/\x02{1}\x02".format(x['averagerating'], x['maxrating'])
				info += " - \x02{0}\x02 Views".format(x['viewCount'])
				info += " - \x02{0}\x02 Likes".format(x['numLikes'])
				info += " - \x02{0}\x02 Dislikes".format(x['numDislikes'])
				self.IRC.say(data[2], info)
			else:
				pass

	def YouTubeGetVids(self, data):
		if Lock.Locked:
			self.IRC.notice(data[0].split('!')[0], "Please wait a few seconds before using this command again.")
			return None
		try:
			terms = "+".join(data[4:]).replace("|","%7C")
		except Exception:
			self.IRC.say(data[2], "Supply some searchterms you derp!")
		for vid in self.Search(terms, results=3):
			self.IRC.say(data[2], vid)
		Lock.Lock()

	def Load(self):
		self.Parser.hookCommand("PRIVMSG", self.__name__
			,{"(?:https?:\/\/)?(?:www\.)?youtube\.com\/.*?": self.YouTubeStats
			,"^@yt .*?$": self.YouTubeGetVids}
		)

	def Unload(self):
		pass
	def Reload(self):
		pass

