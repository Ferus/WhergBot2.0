#!/usr/bin/env python
import requests
import re

from .Settings import Settings

class Imgur(object):
	def __init__(self):
		pass
	def ImgurParser(self, html, link):
		'''Obtain ALL the stats!'''
		html = html.replace("\t","").replace("\n","")
		stats = {}
		try:
			stats['title'] = re.findall("<h2>(.*?)</h2>", html)[0]
		except:
			stats['title'] = "No title found."
		if re.findall("<div class=\"info textbox nobottom\">", html): #Linked image wasnt really in the gallery, Also, Errors.
			stats['submitted'] = re.findall("<span id=\"nicetime\" .*?>(.*?)</span>", html)[0]
			stats['views'] = re.findall("<span id=\"views\">([0-9]{1,})</span>", html)[0]
			stats['bandwidth'] = re.findall("<span id=\"bandwidth\">(.*?)</span>", html)[0]
		else:
			tmp = re.findall("\"points-[a-zA-Z0-9]{5}\">[0-9]{1,}</span>.*?</div>", html.replace(",",""))[0].split(":")
			stats['points'] = tmp[0].split("</span>")[0].split("\">")[1]

			likes = re.findall("positive \" title=\".*?\" style=\".*?%\"></div>", html)[0]
			likes, likespercent = likes.split(" \" title=\"")[1].split("\"></div>")[0].split(" likes\" style=\"width: ")
			stats['likes'] = likes
			stats['likespercent'] = str(likespercent)[0:4]

			dislikes = re.findall("negative \" title=\".*?\" style=\".*?%\"></div>", html)[0]
			dislikes, dislikespercent = dislikes.split(" \" title=\"")[1].split("\"></div>")[0].split(" dislikes\" style=\"width: ")
			stats['dislikes'] = dislikes
			stats['dislikespercent'] = str(dislikespercent)[0:4]

			stats['submitted'] = re.findall("<strong>(Submitted .*? ago)</strong>", html)[0]

			v, bw = re.findall("<strong><span class=\"stat\">.*?</span> .*?</strong>", html)
			stats['views'] = v.split("</span>")[0].split("\"stat\">")[1]
			stats['bandwidth'] = bw.split("</span>")[0].split("\"stat\">")[1]

		return stats

	def Fetch(self, ID):
		'''Fetch HTML, Returns a dict from the Parser'''
		link = "http://imgur.com/gallery/{0}".format(ID)
		html = requests.get(link)
		if html.status_code != 200:
			return "Couldn't connect to Imgur"
		return self.ImgurParser(html.content, link)

class Main(Imgur):
	def __init__(self, Name, Parser):
		Imgur.__init__(self)
		self.__name__ = Name
		self.Parser = Parser
		self.IRC = self.Parser.IRC

	def ImgurStats(self, data):
		ImageIds = re.findall('(?:https?:\/\/)?(?:www\.)?(?:i\.)?imgur\.com\/(?:gallery\/)?([a-zA-Z0-9]{5})(?:\.)?(?:jpg|jpeg|png|gif)?', " ".join(data[3:]))
		ImageIds = list(set(ImageIds)) # Remove Duplicates.
		if len(ImageIds) > 3: # Limit polling to the first 3 images if multiple were linked.
			del ImageIds[3:]
		for ID in ImageIds:
			stats = self.Fetch(ID)
			x = "\x02[Imgur]\x02 {0}".format(stats['title'] if stats['title'] else '')
			x += " \x02{0}\x02 views".format(stats['views']) if stats['views'] else ''
			x += " \x02{0}\x02 bandwidth".format(stats['bandwidth']) if stats['bandwidth'] else ''
			x += " \x02{0}\x02".format(stats['submitted']) if stats['submitted'] else ''

			#Tail end.
			x += " - \x02{0}\x02 Points".format(stats['points']) if stats['points'] else ''
			x += " - Likes: \x02{0}\x02/\x02{1}\x02%".format(stats['likes'],stats['likespercent']) \
				if stats['likes'] and stats['likespercent'] else ''
			x += " - Dislikes: \x02{0}\x02/\x02{1}\x02%".format(stats['dislikes'],stats['dislikespercent']) \
				if stats['dislikes'] and stats['dislikespercent'] else ''
			self.IRC.say(data[2], x)

	def Load(self):
		self.Parser.hookCommand('PRIVMSG', "(?:https?:\/\/)?(?:www\.)?(?:i\.)?imgur\.com\/(?:gallery\/)?[a-zA-Z0-9]{5}(?:\.)?(?:jpg|jpeg|png|gif)?", self.ImgurStats)
		self.Parser.hookPlugin(self.__name__, Settings, self.Load, self.Unload, self.Reload)

	def Unload(self):
		pass
	def Reload(self):
		pass
