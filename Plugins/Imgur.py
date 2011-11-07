#!/usr/bin/python2

import requests, re, htmldecode

class Imgur(object):
	def __init__(self):
		pass
	def Parser(self, html):
		'''Obtain ALL the stats!'''
		html = htmldecode.convert(html.replace("\t","").replace("\n",""))
		stats = {}
		stats['link'] = re.findall("http:\/\/(?:www\.)?(?:i\.)?imgur\.com\/(?:gallery\/)?[a-zA-Z0-9]{5}(?:\.)?(?:jpg|jpeg|png|gif)?", html)[0]
		stats['title'] = re.findall("<h2>.*?</h2>", html)[0].replace("<h2>","").replace("</h2>","")

		if re.findall("<div class=\info textbox nobottom\">", html): #Linked image wasnt really in the gallery, Also, Errors.
			stats['submitted'] = re.findall("<span id=\"nicetime\" .*?>.*?</span>", html)[0].split("\">")[1].split("<")[0]
			stats['views'] = re.findall("<span id=\"views\">[0-9]{1,}</span>", html)[0].split("\">")[1].split("<")[0]
			stats['bandwidth'] = re.findall("<span id=\"bandwidth\">.*</span>", html)[0].split("\">")[1].split("<")[0]
			print("3")
		else:
			tmp = re.findall("\"points-[a-zA-Z0-9]{5}\">[0-9]{1,}</span>.*?</div>", html)[0].split(":")
			stats['points'] = tmp[0].split("</span>")[0].split("\">")[1]

			likes = re.findall("positive \" title=\".*?\" style=\".*?%\"></div>", html)[0]
			likes, likespercent = likes.split(" \" title=\"")[1].split("\"></div>")[0].split(" likes\" style=\"width: ")
			stats['likes'] = likes
			stats['likespercent'] = str(likespercent)[0:4]

			dislikes = re.findall("negative \" title=\".*?\" style=\".*?%\"></div>", html)[0]
			dislikes, dislikespercent = dislikes.split(" \" title=\"")[1].split("\"></div>")[0].split(" dislikes\" style=\"width: ")
			stats['dislikes'] = dislikes
			stats['dislikespercent'] = str(dislikespercent)[0:4]

			s = re.findall("<strong>Submitted .*? hours ago</strong>", html)[0]
			stats['submitted'] = s.split("</strong>")[0].split("<strong>")[1]

			v, bw = re.findall("<strong><span class=\"stat\">.*?</span> .*?</strong>", html)
			stats['views'] = v.split("</span>")[0].split("\"stat\">")[1]
			stats['bandwidth'] = bw.split("</span>")[0].split("\"stat\">")[1]

		return stats
	
	def Main(self, link):
		'''Fetch HTML, Returns a dict from the Parser'''
		if not re.search("gallery", link): #Convert to gallery link.
			picId = re.findall("\/[a-zA-Z0-9]{5}\.(?:jpg|png|jpeg|gif)", link)[0][0:6]
			link = "http://imgur.com/gallery{0}".format(picId)
		html = requests.get(link)
		if html.status_code != 200:
			return "Couldn't connect to Imgur"
		return self.Parser(html.content)
