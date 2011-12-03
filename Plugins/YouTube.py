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

		minutes, seconds = divmod(int(jsonReply['entry']['media$group']['yt$duration']['seconds']), 60)
		hours, minutes = divmod(minutes, 60)
		duration = ""
		if hours != 0:
			duration += "{0}:".format(str(hours).zfill(2))
		duration += "{0}:{1}".format(str(minutes).zfill(2), str(seconds).zfill(2))

		stats = {
		'title':convert(title),
		'author':convert(str(jsonReply['entry']['author'][0]['name']['$t'])),
		
		'averagerating':D(jsonReply['entry']['gd$rating']['average']).quantize(TWOPLACES),
		'maxrating':int(jsonReply['entry']['gd$rating']['max']),
		'percentrating':perc,
		'totalvotes':totalvotes,
		'likes':likes,
		'dislikes':dislikes,
		
		'duration':duration,
		'viewcount':"{:1,}".format(int(jsonReply['entry']['yt$statistics']['viewCount'])),
		'favorites':int(jsonReply['entry']['yt$statistics']['favoriteCount']),
		}
		return stats

YouTube = YT()

def youtubestats(msg, sock, users, allowed):
	vidId = re.findall("=[a-zA-Z0-9_\-]{11}", msg[4])[0][1:]
	x = YouTube.Main(vidId)
	if x != None:
	# [YouTube] title - By: author {duration} <averagerating/maxrating (percentrating%)> [x Likes/x Dislikes/x Total]
		head = "\x02[YouTube]\x02 {0} - By: \x02{1}\x02 [\x02{2}\x02]".format(x['title'], x['author'], str(x['duration']))
		middle = "<\x02{0}\x02/\x02{1}\x02 (\x02{2}%\x02) \x02{3}\x02 Views>".format(str(int(x['averagerating'])), str(x['maxrating']), str(x['percentrating'])[2:], str(x['viewcount']))
		tail = "[\x02{0}\x02 Likes/\x02{1}\x02 Dislikes/\x02{2}\x02 Total]".format(str(x['likes']), str(x['dislikes']), str(x['totalvotes']))
		
		y = "{0} {1} {2}".format(head, middle, tail)
		sock.say(msg[3], y)
	else:
		pass
		
hooks = {
	'(?:https?:\/\/)?(?:www\.)?youtube\.com\/watch': [youtubestats, 5, False],	
		}

#TODO - 'https://gdata.youtube.com/feeds/api/videos?q={0}&safeSearch=none&max-results=2&v=2&alt=json'
#"+".join(searchTerm.replace("|","%7C").replace("  "," "))

#{u'author': [{u'name': {u'$t': u'YouTube'},
#             u'uri': {u'$t': u'http://www.youtube.com/'}}],
#u'category': [{u'scheme': u'http://schemas.google.com/g/2005#kind',
#               u'term': u'http://gdata.youtube.com/schemas/2007#video'}],
#u'entry': [{u'author': [{u'name': {u'$t': u'NewWorld187TV'},
#                         u'uri': {u'$t': u'https://gdata.youtube.com/feeds/api/users/newworld187tv'}}],
#            u'category': [{u'scheme': u'http://schemas.google.com/g/2005#kind',
#                           u'term': u'http://gdata.youtube.com/schemas/2007#video'},
#                          {u'label': u'Music',
#                           u'scheme': u'http://gdata.youtube.com/schemas/2007/categories.cat',
#                           u'term': u'Music'},
#                          {u'scheme': u'http://gdata.youtube.com/schemas/2007/keywords.cat',
#                           u'term': u'Twizted'},
#                          {u'scheme': u'http://gdata.youtube.com/schemas/2007/keywords.cat',
#                           u'term': u'New'},
#                          {u'scheme': u'http://gdata.youtube.com/schemas/2007/keywords.cat',
#                           u'term': u'World'},
#                          {u'scheme': u'http://gdata.youtube.com/schemas/2007/keywords.cat',
#                           u'term': u'187'},
#                          {u'scheme': u'http://gdata.youtube.com/schemas/2007/keywords.cat',
#                           u'term': u'TV'}],
#            u'content': {u'src': u'https://www.youtube.com/v/2cW3EX2EOkw?version=3&f=videos&app=youtube_gdata',
#                         u'type': u'application/x-shockwave-flash'},
#            u'gd$comments': {u'gd$feedLink': {u'countHint': 77,
#                                              u'href': u'https://gdata.youtube.com/feeds/api/videos/2cW3EX2EOkw/comments?v=2'}},
#            u'gd$etag': u'W/"CUQCSX47eCp7I2A9WhRSGEk."',
#            u'gd$rating': {u'average': 4.3488374,
#                           u'max': 5,
#                           u'min': 1,
#                           u'numRaters': 86,
#                           u'rel': u'http://schemas.google.com/g/2005#overall'},
#            u'id': {u'$t': u'tag:youtube.com,2008:video:2cW3EX2EOkw'},
#            u'link': [{u'href': u'https://www.youtube.com/watch?v=2cW3EX2EOkw&feature=youtube_gdata',
#                       u'rel': u'alternate',
#                       u'type': u'text/html'},
#                      {u'href': u'https://gdata.youtube.com/feeds/api/videos/2cW3EX2EOkw/responses?v=2',
#                       u'rel': u'http://gdata.youtube.com/schemas/2007#video.responses',
#                       u'type': u'application/atom+xml'},
#                      {u'href': u'https://gdata.youtube.com/feeds/api/videos/2cW3EX2EOkw/related?v=2',
#                       u'rel': u'http://gdata.youtube.com/schemas/2007#video.related',
#                       u'type': u'application/atom+xml'},
#                      {u'href': u'https://m.youtube.com/details?v=2cW3EX2EOkw',
#                       u'rel': u'http://gdata.youtube.com/schemas/2007#mobile',
#                       u'type': u'text/html'},
#                      {u'href': u'https://gdata.youtube.com/feeds/api/videos/2cW3EX2EOkw?v=2',
#                       u'rel': u'self',
#                       u'type': u'application/atom+xml'}],
#            u'media$group': {u'media$category': [{u'$t': u'Music',
#                                                  u'label': u'Music',
#                                                  u'scheme': u'http://gdata.youtube.com/schemas/2007/categories.cat'}],
#                             u'media$content': [{u'duration': 227,
#                                                 u'expression': u'full',
#                                                 u'isDefault': u'true',
#                                                 u'medium': u'video',
#                                                 u'type': u'application/x-shockwave-flash',
#                                                 u'url': u'https://www.youtube.com/v/2cW3EX2EOkw?version=3&f=videos&app=youtube_gdata',
#                                                 u'yt$format': 5},
#                                                {u'duration': 227,
#                                                 u'expression': u'full',
#                                                 u'medium': u'video',
#                                                 u'type': u'video/3gpp',
#                                                 u'url': u'rtsp://v4.cache7.c.youtube.com/CiILENy73wIaGQlMOoR9EbfF2RMYDSANFEgGUgZ2aWRlb3MM/0/0/0/video.3gp',
#                                                 u'yt$format': 1},
#                                                {u'duration': 227,
#                                                 u'expression': u'full',
#                                                 u'medium': u'video',
#                                                 u'type': u'video/3gpp',
#                                                 u'url': u'rtsp://v4.cache6.c.youtube.com/CiILENy73wIaGQlMOoR9EbfF2RMYESARFEgGUgZ2aWRlb3MM/0/0/0/video.3gp',
#                                                 u'yt$format': 6}],
#                             u'media$credit': [{u'$t': u'NewWorld187TV',
#                                                u'role': u'uploader',
#                                                u'scheme': u'urn:youtube'}],
#                             u'media$description': {u'$t': u'awsome song',
#                                                    u'type': u'plain'},
#                             u'media$keywords': {u'$t': u'Twizted, New, World, 187, TV'},
#                             u'media$license': {u'$t': u'youtube',
#                                                u'href': u'http://www.youtube.com/t/terms',
#                                                u'type': u'text/html'},
#                             u'media$player': {u'url': u'https://www.youtube.com/watch?v=2cW3EX2EOkw&feature=youtube_gdata_player'},
#                             u'media$restriction': [{u'$t': u'DE',
#                                                     u'relationship': u'deny',
#                                                     u'type': u'country'}],
#                             u'media$thumbnail': [{u'height': 90,
#                                                   u'time': u'00:01:53.500',
#                                                   u'url': u'http://i.ytimg.com/vi/2cW3EX2EOkw/default.jpg',
#                                                   u'width': 120,
#                                                   u'yt$name': u'default'},
#                                                  {u'height': 360,
#                                                   u'url': u'http://i.ytimg.com/vi/2cW3EX2EOkw/hqdefault.jpg',
#                                                   u'width': 480,
#                                                   u'yt$name': u'hqdefault'},
#                                                  {u'height': 90,
#                                                   u'time': u'00:00:56.750',
#                                                   u'url': u'http://i.ytimg.com/vi/2cW3EX2EOkw/1.jpg',
#                                                   u'width': 120,
#                                                   u'yt$name': u'start'},
#                                                  {u'height': 90,
#                                                   u'time': u'00:01:53.500',
#                                                   u'url': u'http://i.ytimg.com/vi/2cW3EX2EOkw/2.jpg',
#                                                   u'width': 120,
#                                                   u'yt$name': u'middle'},
#                                                  {u'height': 90,
#                                                   u'time': u'00:02:50.250',
#                                                   u'url': u'http://i.ytimg.com/vi/2cW3EX2EOkw/3.jpg',
#                                                   u'width': 120,
#                                                   u'yt$name': u'end'}],
#                             u'media$title': {u'$t': u'Twizted-story of our lives',
#                                              u'type': u'plain'},
#                             u'yt$duration': {u'seconds': u'227'},
#                             u'yt$uploaded': {u'$t': u'2008-11-16T23:46:26.000Z'},
#                             u'yt$videoid': {u'$t': u'2cW3EX2EOkw'}},
#            u'published': {u'$t': u'2008-11-16T23:46:26.000Z'},
#            u'title': {u'$t': u'Twizted-story of our lives'},
#            u'updated': {u'$t': u'2011-11-21T02:42:48.000Z'},
#            u'yt$accessControl': [{u'action': u'comment',
#                                   u'permission': u'allowed'},
#                                  {u'action': u'commentVote',
#                                   u'permission': u'allowed'},
#                                  {u'action': u'videoRespond',
#                                   u'permission': u'moderated'},
#                                  {u'action': u'rate',
#                                   u'permission': u'allowed'},
#                                  {u'action': u'embed',
#                                   u'permission': u'allowed'},
#                                  {u'action': u'list',
#                                   u'permission': u'allowed'},
#                                  {u'action': u'autoPlay',
#                                   u'permission': u'allowed'},
#                                  {u'action': u'syndicate',
#                                   u'permission': u'allowed'}],
#            u'yt$rating': {u'numDislikes': u'14', u'numLikes': u'72'},
#            u'yt$statistics': {u'favoriteCount': u'214',
#                               u'viewCount': u'46459'}},
#u'gd$etag': u'W/"D0INRHwycSp7I2A9WhRRGU0."',
#u'generator': {u'$t': u'YouTube data API',
#               u'uri': u'http://gdata.youtube.com',
#               u'version': u'2.1'},
#u'id': {u'$t': u'tag:youtube.com,2008:videos'},
#u'link': [{u'href': u'https://www.youtube.com',
#           u'rel': u'alternate',
#           u'type': u'text/html'},
#          {u'href': u'https://gdata.youtube.com/feeds/api/videos?alt=json&q=Twiztid&start-index=1&max-results=2&safeSearch=none&oi=spell&spell=1&v=2',
#           u'rel': u'http://schemas.google.com/g/2006#spellcorrection',
#           u'title': u'Twiztid',
#           u'type': u'application/atom+xml'},
#          {u'href': u'https://gdata.youtube.com/feeds/api/videos?v=2',
#           u'rel': u'http://schemas.google.com/g/2005#feed',
#           u'type': u'application/atom+xml'},
#          {u'href': u'https://gdata.youtube.com/feeds/api/videos/batch?v=2',
#           u'rel': u'http://schemas.google.com/g/2005#batch',
#           u'type': u'application/atom+xml'},
#          {u'href': u'https://gdata.youtube.com/feeds/api/videos?alt=json&q=Twizted&start-index=1&max-results=2&safeSearch=none&v=2',
#           u'rel': u'self',
#           u'type': u'application/atom+xml'},
#          {u'href': u'https://gdata.youtube.com/feeds/api/videos?alt=atom-service&v=2',
#           u'rel': u'service',
#           u'type': u'application/atomsvc+xml'},
#          {u'href': u'https://gdata.youtube.com/feeds/api/videos?alt=json&q=Twizted&start-index=3&max-results=2&safeSearch=none&v=2',
#           u'rel': u'next',
#           u'type': u'application/atom+xml'}],
#u'logo': {u'$t': u'http://www.youtube.com/img/pic_youtubelogo_123x63.gif'},
#u'openSearch$itemsPerPage': {u'$t': 2},
#u'openSearch$startIndex': {u'$t': 1},
#u'openSearch$totalResults': {u'$t': 6003},
#u'title': {u'$t': u'YouTube Videos matching query: Twizted'},
#u'updated': {u'$t': u'2011-12-03T09:46:35.299Z'},
#u'xmlns': u'http://www.w3.org/2005/Atom',
#u'xmlns$gd': u'http://schemas.google.com/g/2005',
#u'xmlns$media': u'http://search.yahoo.com/mrss/',
#u'xmlns$openSearch': u'http://a9.com/-/spec/opensearch/1.1/',
#u'xmlns$yt': u'http://gdata.youtube.com/schemas/2007'}
