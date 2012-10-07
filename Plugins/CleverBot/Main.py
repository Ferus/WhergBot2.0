#!/usr/bin/env python

from threading import Thread

from . import cleverbot
from .Settings import Settings

class Main():
	def __init__(self, Name, Parser):
		self.__name__ = Name
		self.Parser = Parser
		self.IRC = self.Parser.IRC
		self.Running = False
		self.Cleverbot = None
		self.activeChannel = ''

	def initCleverbot(self, data):
		"""Called on @cleverbot
		Checks if we're in an allowed channel and if we're already running."""
		if data[2] not in Settings.get('allowedChans'):
			return None
		if self.Running:
			return None
		self.activeChannel = data[2]
		self.Cleverbot = cleverbot.Session()
		self.Running = True
		self.IRC.say(data[2], "\x02[CleverBot]\x02 Connecting to Cleverbot.")
		reply = self.Cleverbot.Ask(' '.join(data[4:]))
		self.IRC.say(data[2], "\x02[CleverBot]\x02 CleverBot -> {0}: {1}".format(
			data[0].split("!")[0], reply))

	def sendMessage(self, data):
		"""Sends a message to cleverbot"""
		if data[2] not in Settings.get('allowedChans'):
			return None
		if not self.Running:
			self.IRC.say(data[2], "\x02[CleverBot]\x02 Not connected!")
			return None
		msg = ' '.join(data[3:])[2:]
		print("* [CleverBot] Sending Message: '{0}'".format(msg))
		self.IRC.say(data[2], "\x02[CleverBot]\x02 {0} -> CleverBot: {1}".format(
			data[0].split("!")[0], msg))
		def helper(msg):
			# Threads replys, prevents 'lag'
			reply = self.Cleverbot.Ask(msg)
			self.IRC.say(data[2], "\x02[CleverBot]\x02 CleverBot -> {0}: {1}".format(
				data[0].split("!")[0], reply))
		t = Thread(target=helper, args=(msg,))
		t.daemon = True
		t.start()

	def disconnect(self, data):
		"""Sends a nice goodbye message and cleans up"""
		if data[2] not in Settings.get('allowedChans'):
			return None
		if not self.Running:
			return None
		reply = self.Cleverbot.Ask("Goodbye! :<")
		self.IRC.say(data[2], "\x02[CleverBot]\x02 {0}".format(reply))
		# cleanup
		self.Cleverbot = None
		self.Running = False
		self.activeChannel = ''

	def Load(self):
		self.Parser.hookCommand("PRIVMSG", "^@cleverbot .+$", self.initCleverbot)
		self.Parser.hookCommand("PRIVMSG", "^!.+$", self.sendMessage)
		self.Parser.hookCommand("PRIVMSG", "^@cleverdc$", self.disconnect)
		self.Parser.hookPlugin(self.__name__, Settings, self.Load, self.Unload, self.Reload)

	def Unload(self):
		pass
	def Reload(self):
		pass

