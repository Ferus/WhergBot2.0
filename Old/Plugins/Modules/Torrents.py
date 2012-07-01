#!/usr/bin/env python

"""
Torrents.py by Ferus (^) @
Opsimathia.datnode.net / Mempsimoiria.datnode.net #hacking
Searches multiple sites for torrents based on 'user input'.

Required: requests - https://github.com/kennethreitz/requests

Currently Supported Websites:
http://thepiratebay.se/
http://demonoid.me/
http://1337x.org/
http://kat.ph/

Each Request() call from every class
returns a dict with the following keys:

	title - The title of the torrent
	seed - The number of seeders
	leech - The number of leechers
	size - Size of the torrent
	link - http link to the .torrent file
		empty string if not found
	magnetlink - magnet link to torrent

However if we fail to get html, we raise requests.HTTPError
and return the error string.
"""

"""
Released under the hLP v2 licence:

dis iz hPL v2
imho u shud uz hPL v2 but idfc mang u can uz hPL v1 i guss

this is da h public license
best license ever imho l0l
^ tbqhz

rools of da h public license (frum her on out nown az h)
1. do whatever the fuck you want man idfk tbh imho
2. fk off copyright lawyers
3. gtfo my software copyright lawyers
4. lmao u got 0wn3d xD
5. l0l
6. (imho) (tbh) (l0l)
7. hunter is cool l0l
8. h
9. h
11. h
12. u cant get made at mi 4 nt havn a #10 l0l
"""

try:
	import requests
except ImportError:
	import sys
	sys.exit("This script requires requests to be installed.")

import re

class MissingTermsError(Exception):
	"""You failed to pass any searchterms."""

class MissingCategoryError(Exception):
	"""That category does not exist."""

class DefaultSearch(object):
	def __init__(self):
		self.SearchURL = ""
		self.SearchCategories = {}
		self.WhiteSpaceRegex = "\t|\n"
		self.TorrentGroupRegex = ""

		self.REGEXES = {"title": ["", 0]
			,"link": ["", 0]
			,"magnetlink": ["", 0]
			,"seed": ["", 0]
			,"leech": ["", 0]
			,"size": ["", 0]}

	def Request(self, terms, category='all'):
		if not terms:
			raise MissingTermsError
		if category not in self.SearchCategories.keys():
			raise MissingCategoryError
		url = self.SearchURL.format(terms, self.SearchCategories[category])

		try:
			req = requests.get(url)
			if req.status_code != 200:
				raise requests.HTTPError
			return self.Parse(req.content)
		except requests.HTTPError, e:
			return e.message

	def Parse(self, html):
		torrentdict = {}
		html = re.sub(self.WhiteSpaceRegex, "", html)
		torrents = re.findall(self.TorrentGroupsRegex, html)
		x = 0
		while len(torrents) != 0:
			torrent = torrents.pop(0)
			info = {}
			for regex in self.REGEXES.keys():
				try:
					info[regex] = re.findall(self.REGEXES[regex][0], torrent)[self.REGEXES[regex][1]]
				except IndexError:
					info[regex] = ""
				except Exception, e:
					info[regex] = "Error: {0}".format(repr(e))
			torrentdict[str(x)] = info
			x += 1
		return torrentdict

class ThePirateBaySearch(DefaultSearch):
	"""Poll ThePirateBay.
	"""
	def __init__(self):
		self.SearchURL = "http://thepiratebay.se/search/{0}/0/99/{1}" # Terms, Category.
		self.SearchCategories = {
			'all': '0'

			# Audio
			,'music': '101'
			,'audio books': '102'
			,'sound clips': '103'
			,'flac': '104'

			# Video
			,'movies': '201'
			,'movies dvdr': '202'
			,'music videos': '203'
			,'movie clips': '204'
			,'tv shows': '205'
			,'handheld': '206'
			,'highres movies': '207'
			,'highres tv shows': '208'
			,'3d': '209'

			# Applications
			,'windows': '301'
			,'mac': '302'
			,'unix': '303'
			,'handheld': '304'
			,'ios': '305'
			,'android': '306'

			# Games
			,'pc games': '401'
			,'mac games': '402'
			,'psx': '403'
			,'xbox360': '404'
			,'wii': '405'
			,'handheld games': '406'
			,'ios games': '407'
			,'android games': '408'

			# Porn
			,'porn movies': '501'
			,'porn movies dvdr': '502'
			,'porn pictures': '503'
			,'porn games': '504'
			,'porn highres movies': '505'
			,'porn movie clips': '506'

			# Other
			,'e-books': '601'
			,'comics': '602'
			,'pictures': '603'
			,'covers': '604'
			,'physibles': '605'}

		self.WhiteSpaceRegex = "\t|\n"
		self.TorrentGroupsRegex = "<tr>(.*?)</tr>"

		self.REGEXES = {"title": ["<div class=\"detName\"><a .*?>(.*?)</a>", 0]
			,"link": ["<a href=\"(http.*?)\" title=\"Download this torrent\">", 0]
			,"magnetlink": ["<a href=\"(magnet:.*?)\" title=\"Download this torrent using magnet\">", 0]
			,"seed": ["<td align=\"right\">(.*?)</td>", 0]
			,"leech": ["<td align=\"right\">(.*?)</td>", 1]
			,"size": ["<font class=\"detDesc\">.*?(Size .*?), ULed by <a.*?</a></font>", 0]}

class leetxSearch(object):
	def __init__(self):
		self.SearchURL = "http://1337x.org/search/{0}/{1}/" # Terms, Page

	def Parse(self, html):
		torrentdict = {}
		html = re.sub('\s{2,}', ' ', html.replace("\t", "").replace("\n", ""))
		torrents = re.findall("<div class=\"torrentName\">(.*?)</div> <div class=\"clr\"></div>", html)
		x = 0
		while len(torrents) != 0:
			torrent = torrents.pop(0)
			info = {}
			page, info['title'] = re.findall("<a href=\"(/torrent/.*?)\" class=\"org\">(.*?)</a>", torrent)[0]
			info['leech'] = re.findall("<span class=\"leech\">(.*?)</span>", torrent)[0]
			info['seed'] = re.findall("<span class=\"seed\">(.*?)</span>", torrent)[0]
			info['size'] = re.findall("<span class=\"size\">(.*?)</span>", torrent)[0]

			newhtml = requests.get("http://1337x.org"+page)
			if newhtml.status_code != 200:
				info['link'] = None
				info['magnetlink'] = None
			else:
				newhtml = newhtml.content
				info['link'] = "http://1337x.org" + re.findall("<a href=\"(/download/.*?)\" class=\"torrentDw\" title=\"Torrent Download\"></a>", newhtml)[0]
				info['magnetlink'] = re.findall("<a href=\"(magnet.*?)\" class=\"magnetDw\" title=\"Magnet Download\"></a>", newhtml)[0]
			torrentdict[str(x)] = info
			x += 1
		return torrentdict

	def Request(self, terms, page=0):
		if not terms:
			raise MissingTermsError
		url = self.SearchURL.format(terms, page)

		try:
			req = requests.get(url)
			if req.status_code != 200:
				raise requests.HTTPError
			return self.Parse(req.content)
		except requests.HTTPError, e:
			return e.message

class KickAssTorrentsSearch(DefaultSearch):
	def __init__(self):
		self.SearchURL = "http://kat.ph/usearch/{0}{1}" # Terms
		self.SearchCategories = {"all": ""
			,"applications": "/?categories[]=applications"
			,"books": "/?categories[]=books"
			,"games": "/?categories[]=games"
			,"movies": "/?categories[]=movies"
			,"music": "/?categories[]=music"
			,"tv": "/?categories[]=tv"
			,"xxx": "/?categories[]=xxx"
			,"other": "/?categories[]=other"}

		self.WhiteSpaceRegex = "\t|\n|<strong class=\"red\">|</strong>|<span>|</span>"
		self.TorrentGroupsRegex = "<tr class=\"(?:even|odd)\" id=\".*?\">(.*?)</tr>"

		self.REGEXES = {"title": ["<a href=\".*?\" class=\"normalgrey font12px plain bold\">(.*?)</a>", 0]
			,"link": ["<a title=\"Download torrent file\" href=\"(.*?)\".*?>", 0]
			,"magnetlink": ["<a title=\"Torrent magnet link\" href=\"(magnet.*?)\" .*?class=\"imagnet icon16\">", 0]
			,"seed": ["<td class=\"green center\">(.*?)</td>", 0]
			,"leech": ["<td class=\"red lasttd center\">(.*?)</td>", 0]
			,"size": ["<td class=\"nobr center\">(.*?)</td>", 0]}

class DemonoidSearch(DefaultSearch):
	def __init__(self):
		self.SearchURL = "http://beta.demonoid.me/files/?query={0}&sort=&category={1}&external=2&quality=0" # terms, category
		self.SearchCategories = {"all": ""
			,"movies": "1"
			,"music": "2"
			,"tv": "3"
			,"games": "4"
			,"applications": "5"
			,"misc": "6"
			,"pictures": "8"
			,"anime": "9"
			,"comics": "10"
			,"books": "11"
			,"music videos": "13"
			,"audio books": "17"}

		self.WhiteSpaceRegex = "\t|\n"
		self.TorrentGroupsRegex = "<tr(?:.*?class=\"alt\".*?)? id=\"atorr[0-9]{0,}\">(.*?</tr>.*?)</tr>"

		self.REGEXES = {"title": ["<a href=\"http://beta.demonoid.me/files/details/.*?/.*?\" class=\"bl\">(.*?)(?: <span.*?</span>)?</a>", 0]
			,"link": ["<a href=\"(http://beta.demonoid.me/files/download/.*?/)\" class=\"download\">", 0]
			,"magnetlink": ["<a href=\"(http://beta.demonoid.me/files/downloadmagnet/.*?/)\" class=\"download\">", 0]
			,"seed": ["<td class=\"tseeders\">(.*?)</td>", 0]
			,"leech": ["<td class=\"tleechers\">(.*?)</td>", 0]
			,"size": ["<td class=\"tsize\">(.*?)</td>", 0]}

def Test():
	from pprint import pprint
	#tpb = ThePirateBaySearch()
	#pprint(tpb.Request("House", "tv shows"))

	#leetx = leetxSearch()
	#pprint(leetx.Request("House"))

	#kat = KickAssTorrentsSearch()
	#pprint(kat.Request("House", "tv"))

	#dem = DemonoidSearch()
	#pprint(dem.Request("House", "tv"))
	#print("\n\n\n")
	#pprint(dem.Request("Naruto", "anime"))

if __name__ == '__main__':
	pass
