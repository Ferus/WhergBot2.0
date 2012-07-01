#!/usr/bin/env python
import requests
from htmldecode import convert

class StreamInfo():
	'''A personal script that polls a Shoutcast server.'''
	def __init__(self):
		self.url = "http://opsimathia.datnode.net:8000/index.html?sid=1"
	
	def now_playing(self):
		try:
			info = self.get_html("http://opsimathia.datnode.net:8000/currentsong?sid=1")
			if info:	
				return "NP: {0}".format(info)
			else:
				return "No title found."
		except:
			return "No title found."
	
	def send_url(self):
		return "Stream URL: http://opsimathia.datnode.net:8000/listen.pls"

	def status(self):
		try:
			info = self.get_html(self.url)
			info = info.split("Stream Status: ")[1].split("<b>")[1].split("</b>")[0]
			info = info.replace("up","up")

			listeners = self.get_html(self.url)
			listeners = listeners.split("Listener Peak: ")[1].split("<b>")[1].split("</b>")[0]
			return "Stream Status: {0} and a record of {1} listeners.".format(info, listeners)
		except:
			return "Stream is currently down."

	def title(self):
		try:
			title = self.get_html(self.url)
			title = title.split("Stream Title: ")[1].split("<b>")[1].split("</b>")[0]
			return "Stream Title: {0}".format(title.replace("&apos;","'"))
		except:
			return "Stream is currently down."
			
	def get_html(self, link):
		html = requests.get(link)
		if html.status_code != 200:
			return None
		html = convert(html.content)
		return html
		
S = StreamInfo()		
		
def Stream(msg, sock, users, allowed):
	try:
		if msg[4].split()[1:]:
			Text = msg[4].split()[1:]
		else:
			Text = []
		
		if Text[0] == 'np' or Text[0].lower() == 'now' and Text[1].lower() == 'playing':
			sock.say(msg[3], S.now_playing())
		
		elif Text[0] == 'url':
			sock.say(msg[3], S.send_url())
			
		elif Text[0] == 'status':
			sock.say(msg[3], S.status())
			
		elif Text[0] == 'title':
			sock.say(msg[3], S.title())
			
	except Exception, e:
		print("* [Stream] Error:\n* [Stream] {0}".format(str(e)))
		
hooks = {
	'^@stream': [Stream, 5, False],	
		}
helpstring = """Used with Shoutcast servers to show info.
@stream np/now playing: Shows current song
@stream url: Gives the streams url
@stream status: Gives the streams status
@stream title: Gives the streams title"""
