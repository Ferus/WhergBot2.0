#!/usr/bin/env python

import requests, re, htmldecode

class Imgur(object):
	def __init__(self):
		pass
	def Parser(self, html, link):
		'''Obtain ALL the stats!'''
		html = htmldecode.convert(html.replace("\t","").replace("\n",""))
		stats = {}
		try:
			stats['title'] = re.findall("<h2>.*?</h2>", html)[0].replace("<h2>","").replace("</h2>","")
		except:
			stats['title'] = "No title found."
		if re.findall("<div class=\"info textbox nobottom\">", html): #Linked image wasnt really in the gallery, Also, Errors.
			stats['submitted'] = re.findall("<span id=\"nicetime\" .*?>.*?</span>", html)[0].split("\">")[1].split("<")[0]
			stats['views'] = re.findall("<span id=\"views\">[0-9]{1,}</span>", html)[0].split("\">")[1].split("<")[0]
			stats['bandwidth'] = re.findall("<span id=\"bandwidth\">.*?</span>", html)[0].split("\">")[1].split("<")[0]
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

			s = re.findall("<strong>Submitted .*? ago</strong>", html)[0]
			stats['submitted'] = s.split("</strong>")[0].split("<strong>")[1]

			v, bw = re.findall("<strong><span class=\"stat\">.*?</span> .*?</strong>", html)
			stats['views'] = v.split("</span>")[0].split("\"stat\">")[1]
			stats['bandwidth'] = bw.split("</span>")[0].split("\"stat\">")[1]

		return stats

	def Main(self, ID):
		'''Fetch HTML, Returns a dict from the Parser'''
		link = "http://imgur.com/gallery/{0}".format(ID)
		html = requests.get(link)
		if html.status_code != 200:
			return "Couldn't connect to Imgur"
		return self.Parser(html.content, link)

I = Imgur()

def ImgurStats(msg, sock, users, allowed):

	y = msg[4].replace('gallery/', '')
	Links = [x for x in re.findall('(?:https?:\/\/)?(?:www\.)?(?:i\.)?imgur\.com\/[a-zA-Z0-9]{5}(?:\.)?(?:jpg|jpeg|png|gif)?', y)]
	ImageIds = []
	for Link in Links:
		[ImageIds.append(x) for x in re.findall("[a-zA-Z0-9]{5}", re.sub("(?:https:\/\/)?(:?www\.)?(?:i\.)?imgur\.com\/", "", Link)) if (x not in ImageIds)]
	print ImageIds
	if len(ImageIds) > 3: # Limit polling to the first 3 images.
		del ImageIds[3:]
	for ID in ImageIds:
		stats = I.Main(ID)
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

		sock.say(msg[3], x

hooks = {
	'(?:https?:\/\/)?(?:www\.)?(?:i\.)?imgur\.com\/(?:gallery\/)?[a-zA-Z0-9]{5}(?:\.)?(?:jpg|jpeg|png|gif)?': [ImgurStats, 5, False],
	}

helpstring = """Parses messages for imgur links, and returns statistics of the image."""
