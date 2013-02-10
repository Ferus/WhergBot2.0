#!/usr/bin/env python
#Youtube Stats/Link Parser

import requests
import json
import re

from Parser import Locker
Lock = Locker(5)

import logging
logger = logging.getLogger("YouTube")

class YouTube(object):
	def Main(self, vidId):
		if not vidId:
			return None
		r = requests.get("http://gdata.youtube.com/feeds/api/videos/{0}?alt=json&v=2".format(vidId))
		try:
			r.raise_for_status()
		except (requests.HTTPError, requests.ConnectionError):
			logger.exception("Failed to poll YouTube")
		r = json.loads(r.text)
		return self.Parse(r['entry'])

	def ConvertTime(self, seconds):
		minutes, seconds = divmod(seconds, 60)
		hours, minutes = divmod(minutes, 60)
		duration = ""
		if hours != 0:
			duration += "{0}:".format(str(hours).zfill(2))
		duration += "{0}:{1}".format(str(minutes).zfill(2), str(seconds).zfill(2))
		return duration

	def Parse(self, reply):
		h = {}
		h['author'] = reply['author'][0]['name']['$t']
		h['title'] = reply['title']['$t']
		h['viewCount'] = int(reply['yt$statistics']['viewCount'])
		h['link'] = "https://youtu.be/"+reply['id']['$t'].split(":")[-1]
		h['duration'] = self.ConvertTime(int(reply['media$group']['yt$duration']['seconds']))

		if reply.get('yt$rating'):
			h['averagerating'] = reply['yt$rating'].get('average', None)
			if h['averagerating'] != None:
				h['averagerating'] = "{:.2}".format(h['averagerating'])
			h['maxrating'] = reply['yt$rating'].get('max', None)
			h['numLikes'] = int(reply['yt$rating'].get('numLikes', None))
			h['numDislikes'] = int(reply['yt$rating'].get('numDislikes', None))

		elif reply.get('gd$rating'):
			h['averagerating'] = reply['gd$rating'].get('average', None)
			if h['averagerating'] != None:
				h['averagerating'] = "{:.2}".format(h['averagerating'])
			h['maxrating'] = reply['gd$rating'].get('max', None)
			h['numLikes'] = int(reply['gd$rating'].get('numLikes', None))
			h['numDislikes'] = int(reply['gd$rating'].get('numDislikes', None))

		else:
			h['averagerating'] = None
			h['maxrating'] = None
			h['numRatings'] = None
			h['numLikes'] = None
			h['numDislikes'] = None
		return h

	def Search(self, terms, results=2):
		link = "https://gdata.youtube.com/feeds/api/videos?q={0}&safeSearch=none&max-results={1}&v=2&alt=json".format(terms, results)
		try:
			r = requests.get(link)
			if r.status_code != 200:
				return None
			r = json.loads(r.text)['feed']['entry']
		except Exception as e:
			logger.exception("Failed to get search info")
			return ['\x02[YouTube]\x02 Failed to get info.']

		results = []
		for vidInfo in r:
			vidInfo = self.Parse(vidInfo)
			# <Title + Uploader> [Length] <Link> [Average/Max Likes/Dislikes] <Views>
			info = "\x02[YouTube]\x02 {0}".format(vidInfo['title'])
			info += " - By: \x02{0}\x02".format(vidInfo['author'])
			info += " - [\x02{0}\x02]".format(vidInfo['duration'])
			if (vidInfo['averagerating'] != None and vidInfo['maxrating'] != None):
				info += " [Rating: \x02{0}\x02/\x02{1}\x02]".format(vidInfo['averagerating'], vidInfo['maxrating'])
			if (vidInfo['numLikes'] != None and vidInfo['numDislikes'] != None):
				info += " - \x02{:,}\x02 Likes".format(vidInfo['numLikes'])
				info += " - \x02{:,}\x02 Dislikes".format(vidInfo['numDislikes'])
			info += " - \x02{:,}\x02 Views".format(vidInfo['viewCount'])
			info += " - {0}".format(vidInfo['link'])
			results.append(info)
		return results


class Main(object):
	def __init__(self, Name, Parser):
		self.__name__ = Name
		self.Parser = Parser
		self.IRC = self.Parser.IRC
		self.YT = YouTube()

	def YouTubeLink(self, data):
		vidIds = list(set(re.findall("v=([\w\d_\-]{11})", ' '.join(data[3:]) )))
		for vidId in vidIds:
			self.YouTubeStats(data, vidId)

	def YouTubeShortLink(self, data):
		vidIds = list(set(re.findall("/([\w\d_\-]{11})", " ".join(data[3:]) )))
		for vidId in vidIds:
			self.YouTubeStats(data, vidId)

	def YouTubeStats(self, data, vidId):
			x = self.YT.Main(vidId)
			if x != None:
				info = "\x02[YouTube]\x02 {0}".format(x['title'])
				info += " - By: \x02{0}\x02".format(x['author'])
				info += " [\x02{0}\x02]".format(x['duration'])
				if (x['averagerating'] != None and x['maxrating'] != None):
					info += " - \x02{0}\x02/\x02{1}\x02".format(x['averagerating'], x['maxrating'])
				if (x['numLikes'] != None and x['numDislikes'] != None):
					info += " - \x02{:,}\x02 Likes".format(x['numLikes'])
					info += " - \x02{:,}\x02 Dislikes".format(x['numDislikes'])
				info += " - \x02{:,}\x02 Views".format(x['viewCount'])
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
		for vid in self.YT.Search(terms, results=3):
			self.IRC.say(data[2], vid)
		Lock.Lock()

	def Load(self):
		self.Parser.hookCommand("PRIVMSG", self.__name__
			,{"(?:https?:\/\/)?(?:www\.)?youtube\.com\/.*?": self.YouTubeLink
			,"(?:https?:\/\/)?(?:www\.)?youtu.be/([\w\d_\-]{11})": self.YouTubeShortLink
			,"^@yt .*?$": self.YouTubeGetVids}
		)

	def Unload(self):
		pass
	def Reload(self):
		pass

