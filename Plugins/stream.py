#!/usr/bin/python2
import requests

class Stream():
	url = "http://opsimathia.datnode.net:8000/index.html?sid=1"
	
	def now_playing(self):
		try:
			info = requests.get("http://opsimathia.datnode.net:8000/currentsong?sid=1").content
			if info:	
				return "NP: {0}".format(info)
			else:
				return "No title found."
		except:
			return "No title found."
	
	def send_url(self):
		return "Stream URL: http://opsimathia.datnode.net:8000/"

	def status(self):
		try:
			info = requests.get(self.url).content
			info = info.split("Stream Status: ")[1].split("<b>")[1].split("</b>")[0]
			info = info.replace("up","up")

			listeners = requests.get(self.url).content
			listeners = listeners.split("Listener Peak: ")[1].split("<b>")[1].split("</b>")[0]
			return "Stream Status: {0} and a record of {1} listeners.".format(info, listeners)
		except:
			return "Stream is currently down."

	def title(self):
		try:
			title = requests.get(self.url).content
			title = title.split("Stream Title: ")[1].split("<b>")[1].split("</b>")[0]
			return "Stream Title: {0}".format(title.replace("&apos;","'"))
		except:
			return "Stream is currently down."

