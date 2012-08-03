#!/usr/bin/env python
from time import strftime
import requests

import Config
from .Settings import Settings
from Parser import Locker
Locker = Locker(3)

def get_meme(url):
	'''
	Creates a generator to store memes in a list.
	t is the type of url to retrieve from
	'''
	meme_db = []
	try:
		memes = requests.get(url).content.replace('_','\x02').split("\n")
	except:
		print("{0} [AutoMeme] Error requesting new memes.".format(strftime(Config.Global['timeformat'])))
		return get_meme()
	for meme in memes:
		meme_db.append(meme)
	meme_db.pop()
	return meme_db

def meme(url):
	'''Returns a meme from the list'''
	meme_db = []
	while True:
		if not meme_db:
			print("{0} [AutoMeme] Getting moar memes!".format(strftime(Config.Global['timeformat'])))
			meme_db = get_meme(url)
		memestr = meme_db[0]
		del meme_db[0]
		yield "\x02[AutoMeme]\x02 {0}".format(memestr)

class Main(object):
	def __init__(self, Name, Parser):
		self.__name__ = Name
		self.Parser = Parser
		self.IRC = self.Parser.IRC

		self.RegularMeme = meme(url=Settings.get('urls').get('regular').format(Settings.get('lines')))
		self.HipsterMeme = meme(url=Settings.get('urls').get('hipster').format(Settings.get('lines')))

	def RegMeme(self, data):
		try:
			if not Locker.Locked:
				self.IRC.say(data[2], next(self.RegularMeme))
				Locker.Lock()
				return
			else:
				self.IRC.notice(data[0].split('!')[0], "Please wait a little longer and try again.")
		except Exception, e:
			print("{0} [AutoMeme] Error:\n{0} [AutoMeme] {1}".format(strftime(Config.Global['timeformat']), str(e)))

	def HipMeme(self, data):
		try:
			if not Locker.Locked:
				self.IRC.say(data[2], next(self.HipsterMeme))
				Locker.Lock()
				return
			else:
				self.IRC.notice(data[0].split('!')[0], "Please wait a little longer and try again.")
		except Exception, e:
			print("{0} [AutoMeme] Error:\n{0} [AutoMeme] {1}".format(strftime(Config.Global['timeformat']), str(e)))

	def Load(self):
		self.Parser.hookCommand('PRIVMSG', "^@meme$", self.RegMeme)
		self.Parser.hookCommand('PRIVMSG', "^@hipmeme$", self.HipMeme)
		self.Parser.hookPlugin(self.__name__, Settings, self.Load, self.Unload, self.Reload)

	def Unload(self):
		del self.Parser.loadedPlugins[self.__name__]
		del self.Parser.Commands['PRIVMSG'][1]["^@meme$"]
		del self.Parser.Commands['PRIVMSG'][1]["^@hipmeme$"]
		del self
	def Reload(self):
		pass
