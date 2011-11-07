#!/usr/bin/python2
import requests
from htmldecode import convert

class Stream():
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

