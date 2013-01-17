#!/usr/bin/env python
import logging
logger = logging.getLogger("Omegle")
from . import omegle
from .Settings import Settings

class Main():
	def __init__(self, Name, Parser):
		self.__name__ = Name
		self.Parser = Parser
		self.IRC = self.Parser.IRC
		self.Running = False
		self.Omegle = None

		self.activeChannel = ''

	def createOmegleConnection(self, data):
		"""Called on :omegle"""
		self.Omegle = omegle.Omegle()

		self.Running = True
		self.activeChannel = data[2]

		self.addOmegleHooks()
		self.Omegle.mainLoop()

	def addOmegleHooks(self):
		cb = [['strangerDisconnected', self.strangerDisconnected]
			,['waiting', self.waiting]
			,['clientID', self.clientID]
			,['gotMessage', self.gotMessage]
			,['typing', self.typing]
			,['stoppedTyping', self.stoppedTyping]
			,['connected', self.connected]
			,['count', self.count]
			,['recaptchaRequired', self.recaptchaRequired]
			,['technical reasons', self.technicalReasons]
			]

		scb = [['win', self.win]
			,['fail', self.fail]
			]

		for x, y in cb:
			self.Omegle.hookCallback(x, y)
		for x, y in scb:
			self.Omegle.hookSCallback(x, y)


	def strangerDisconnected(self, msg):
		self.IRC.say(self.activeChannel, "\x02[Omegle]\x02 \x0302Stranger\x03 has disconnected.")
		self.cleanup()

	def waiting(self, msg):
		self.IRC.say(self.activeChannel, "\x02[Omegle]\x02 Waiting for \x0302Stranger\x03.")

	def clientID(self, msg):
		pass

	def gotMessage(self, msg):
		logger.info("Received Message: '{0}'".format([msg]))
		self.IRC.say(self.activeChannel, "\x02[Omegle]\x02 \x0302Stranger:\x03 {0}".format(msg))

	def typing(self, msg):
		self.IRC.say(self.activeChannel, "\x02[Omegle]\x02 * \x0302Stranger\x03 is typing.")

	def stoppedTyping(self, msg):
		self.IRC.say(self.activeChannel, "\x02[Omegle]\x02 * \x0302Stranger\x03 stopped typing.")

	def connected(self, msg):
		self.IRC.say(self.activeChannel, "\x02[Omegle]\x02 Connected to Omegle!")

	def count(self, msg):
		pass

	def recaptchaRequired(self, msg):
		self.IRC.say(self.activeChannel, "\x02[Omegle]\x02 Omegle has put up a captcha! :(")

	def technicalReasons(self, msg):
		self.IRC.say(self.activeChannel, "\x02[Omegle]\x02 Error: technical reasons (Captcha) :(")

	def win(self, msg):
		logger.info("Sent message! :)")
	def fail(self, msg):
		self.IRC.say(self.activeChannel, "\x02[Omegle]\x02 Error: Failed to send message.")


	def cleanup(self):
		self.Omegle = None
		self.Running = False
		self.activeChannel = ''

	def initOmegle(self, data):
		if data[2] not in Settings.get('allowedChans'):
			return None
		if self.Running:
			return None
		if self.createOmegleConnection(data) == None:
			self.IRC.say(data[2], "\x02[Omegle]\x02 Creating Connection to Omegle.")

	def sendMessage(self, data):
		if data[2] not in Settings.get('allowedChans'):
			return None
		if not self.Running:
			self.IRC.say(data[2], "\x02[Omegle]\x02 Not connected!")
			return None
		msg = ' '.join(data[3:])[2:]
		logger.info("Sending Message: '{0}'".format(msg))
		self.Omegle.sendMessage(msg)

	def makeDisconnect(self, data):
		if data[2] not in Settings.get('allowedChans'):
			return None
		if not self.Running:
			return None
		if self.Omegle.disconnect() == True:
			self.cleanup()
		self.IRC.say(data[2], "\x02[Omegle]\x02 Disconnected!")

	def Load(self):
		self.Parser.hookCommand("PRIVMSG", self.__name__
			,{"^@omegle$": self.initOmegle
			,"^[~`].*?$": self.sendMessage
			,"^@disconnect$": self.makeDisconnect}
		)
	def Unload(self):
		pass
	def Reload(self):
		pass







