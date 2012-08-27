#! /usr/bin/env python
from time import sleep
from threading import Thread
try:
	import queue
except ImportError:
	import Queue as queue

from . import pyborg
from .Settings import Settings

class Main(object):
	def __init__(self, Name, Parser):
		self.__name__ = Name
		self.Parser = Parser
		self.IRC = self.Parser.IRC
		self.Queue = queue.Queue()

		self.Pyborg = pyborg.pyborg(settings=Settings.get('gentbot'))
		self.Learning = Settings.get('gentbot').get('learning')
		self.Replyrate = Settings.get('gentbot').get('replyrate')

		self.Main = Thread(target=self.processForever)
		self.Main.daemon = True
		self.Main.start()

	def Load(self):
		self.Parser.hookCommand("PRIVMSG", ".*", self.process)
		self.Parser.hookPlugin(self.__name__, Settings, self.Load, self.Unload, self.Reload)
	def Unload(self):
		self.save()
		del self.Parser.loadedPlugins[self.__name__]
	def Reload(self):
		pass

	def save(self):
		self.Pyborg.save_all()

	def output(self, message, data):
		self.IRC.say(data[2], message)

	def process(self, data):
		body = " ".join(data[3:])[1:]
		owner = 1 if data[0] in Settings.get("allowed") else 0
		if body.startswith("@"):
			pass
		else:
			args = (self, body, self.Replyrate, self.Learning, data, owner)
			self.addToQueue(args)
	
	def addToQueue(self, args):
		self.Queue.put_nowait(args)
	def getFromQueue(self):
		return self.Queue.get()
	
	def processForever(self):
		while True:
			t = Thread(target=self.Pyborg.process_msg, args=self.getFromQueue())
			t.daemon = True
			t.start()
			sleep(.2)

# find out what I can do to minimize threads
# change command handling to @gentbot <command> <args>
# use pyborg.py to convert databases
