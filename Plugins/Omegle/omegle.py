#!/usr/bin/env python
import random
import os
random.seed(os.urandom(50))
import requests
import json
import threading

Servers = ["http://promenade.omegle.com/"
#	,"http://odo-bucket.omegle.com/"
#	,"http://bajor.omegle.com/"
#	,"http://quilt.omegle.com/"
#	,"http://empok-nor.omegle.com/"
#	,"http://ferengi.omegle.com/"
#	,"http://quibbler.omegle.com/"
#	,"http://cardassia.omegle.com/"

	,"http://front3.omegle.com/"
	,"http://front1.omegle.com/"
	,"http://front2.omegle.com/"
	,"http://front4.omegle.com/"
	,"http://qfront1.omegle.com/"
]


class Omegle(object):
	def __init__(self):
		self.url = random.choice(Servers)
		self.sid = None
		self.thread = None
		self.start_url = "start?rcs=1&firstevents=1&spid="

		# recieving
		self.callbacks = {'strangerDisconnected': []
			,'waiting': []
			,'clientID': []
			,'gotMessage': []
			,'typing': []
			,'stoppedTyping': []
			,'connected': []
			,'count': []
			,'question': []
			,'commonLikes': []
			,'recaptchaRequired': []
			,'technical reasons': []
			}

		# sending
		self.scallbacks = {'win': []
			,'fail': []
			}

	def headers(self, isSending=False):
		h = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:16.0) Gecko/16.0 Firefox/16.0a1"
			,"Accept-Charset": "ISO-8859-1,utf-8;q=0.7,*;q=0.3"
			,"Accept-Encoding": "gzip, deflate"
			,"Accept-Language": "en-US,en;q=0.8"
			,"Connection": "keep-alive"
			,"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
			,"Keep-Alive": "300"
			,"Host": self.url
			,"Origin": "http://omegle.com"
			,"Referer": "http://omegle.com/"

			,"Pragma": "no-cache"
			,"DNT": "1"
			}
		if isSending:
			h["Accept"] = "text/javascript, text/html, application/xml, text/xml, */*"
		else:
			h["Accept"] = "text/json"
		return h

	def post(self, page, isSending=False, data={}):
		try:
			request = requests.post(self.url + page, data=data, headers=self.headers(isSending))
		except (requests.HTTPError, requests.ConnectionError):
			return self.post(page, isSending, data)
		except Exception as e:
			print(repr(e))
		return request.text

	def start(self):
		request = self.post(self.start_url, False, {})
		res = json.loads(request)
		self.sid = res['clientID']
		for x in list(res.items()):
			if x[0] == 'events':
				for y in x[1]:
					self.handleEvent(str(y[0]), y[1] if len(y) > 1 else '')
			else:
				self.handleEvent(str(x[0]), x[1] if len(x) > 1 else '')

	def disconnect(self):
		request = self.post("disconnect", True, {"id":self.sid})
		self.sid = None
		self.thread = None
		return True

	def events(self):
		while self.sid != None:
			request = self.post("events", False, {'id': self.sid})
			if request == 'null':
				self.sid = None
				return "Connection Lost."

			res = json.loads(request)
			for x in res:
				self.handleEvent(str(x[0]), x[1] if len(x) > 1 else '')

	def handleEvent(self, event, msg=''):
		if event in list(self.callbacks.keys()):
			for x in self.callbacks[event]:
				x(msg)
		else:
			print("Unhandled event!")
			print(event, msg)

	def hookCallback(self, event, callback):
		if event in list(self.callbacks.keys()):
			#print("* [Omegle] Hooking function {0} into callback {1}".format(callback, event))
			self.callbacks[event].append(callback)

	def hookSCallback(self, event, callback):
		if event in list(self.scallbacks.keys()):
			#print("* [Omegle] Hooking function {0} into scallback {1}".format(callback, event))
			self.scallbacks[event].append(callback)


	def sendMessage(self, msg):
		self.post("typing", True, {'id': self.sid})
		request = self.post("send", True, {'msg': msg, 'id': self.sid})
		if request in list(self.scallbacks.keys()):
			for x in self.scallbacks[request]:
				x(msg)
		else:
			print("Unknown send confirmation {0}".format(request))

	def mainLoop(self):
		self.start()
		self.thread = threading.Thread(target=self.events, args=())
		self.thread.start()
		return True

class OmegleQuestion(Omegle):
	def __init__(self):
		super(OmegleQuestion, self).__init__()
		self.start_url += "&wantsspy=1"

class OmegleInterest(Omegle):
	def __init__(self, interests):
		super(OmegleInterest, self).__init__()
		if interests:
			interests = " ".join(interests).split(',')
			self.start_url += "&topics=" + json.dumps(interests)
	def disconnect(self):
		self.post("stoplookingforcommonlikes", True, {'id':self.sid})
		return super(OmegleInterest, self).disconnect()
