#!/usr/bin/env python
import requests
import logging
from .Settings import Settings
from Parser import Locker
Locker = Locker(3)
logger = logging.getLogger("Meme")

def get_meme(url):
	'''
	Creates a generator to store memes in a list.
	t is the type of url to retrieve from
	'''
	meme_db = []
	try:
		memes = requests.get(url).text.replace('_','\x02').split("\n")
	except Exception as e:
		logging.exception("Error requesting new memes.")
		return
	for meme in memes:
		meme_db.append(meme)
	meme_db.pop()
	return meme_db

def meme(url):
	'''Returns a meme from the list'''
	meme_db = []
	while True:
		if not meme_db:
			logger.info("Getting moar memes!")
			meme_db = get_meme(url)
		memestr = meme_db[0]
		del meme_db[0]
		yield "\x02[AutoMeme]\x02 {0}".format(memestr)

class Main(object):
	def __init__(self, Name, Parser):
		self.__name__ = Name
		self.Parser = Parser
		self.IRC = self.Parser.IRC

		self.RegularMeme = meme("http://api.automeme.net/text?lines={0}".format(Settings.get('lines')))
		self.HipsterMeme = meme("http://api.automeme.net/text?lines={0}&vocab=hipster".format(Settings.get('lines')))

	def RegMeme(self, data):
		if not Locker.Locked:
			self.IRC.say(data[2], next(self.RegularMeme))
			Locker.Lock()
			return
		else:
			self.IRC.notice(data[0].split('!')[0], "Please wait a little longer and try again.")

	def HipMeme(self, data):
		if not Locker.Locked:
			self.IRC.say(data[2], next(self.HipsterMeme))
			Locker.Lock()
			return
		else:
			self.IRC.notice(data[0].split('!')[0], "Please wait a little longer and try again.")

	def Load(self):
		self.Parser.hookCommand('PRIVMSG', self.__name__, {"^@meme$": self.RegMeme
			,"^@hipmeme$": self.HipMeme}
			)

	def Unload(self):
		del self.Parser.loadedPlugins[self.__name__]
		del self.Parser.Commands['PRIVMSG'][1]["Meme"]
	def Reload(self):
		pass
