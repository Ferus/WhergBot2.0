#!/usr/bin/env python
from random import randint
import shelve
import os
import logging

from .Settings import Settings
logger = logging.getLogger("GuessingGame")

class GuessingStats(object):
	'''
	Stats recording for Guessing Game.
	Stats are held in dictionaries.
	Dict['User']['stat'] where stat is the stat you want.

	List of stats per 'player':
	notValid = Number of invalid numbers guessed
	overMax = Number of guesses over the max number
	underMin = Number of guesses under the min (One)
	tooHigh = Number of guesses that were too high
	tooLow = Number of guesses that were too low
	wins = Number of correct guesses

	List of global stats:
	totalWins = Number of total wins across all games.
	totalPlayers = Number of everyone who has ever played, by nick.
		#len(db['Players'])

	A function that gets absolute totals of all players' stats.

{
	'Players': {
		'Ferus': {
			'notValid':0,
			'overMax':0,
		}
		,'ExamplePerson': {
			'notValid':0,
			'overMax':0,
		}
	}
	#Globals
	,{'totalWins':0,
		}
	,{'totalPlayers':len(db['Players'])
		}
}
	#Etc
	'''

	def __init__(self, _StatsDB=None):
		if _StatsDB:
			self._StatsDB = _StatsDB
		else:
			self._StatsDB = "Plugins/GuessingGame/GuessingGameStats.shelve"

		# Check if a shelve file exists, if not, create a blank one.
		if not os.access(self._StatsDB, 6):
			with open(self._StatsDB, 'w'):
				pass

		_db = shelve.open(self._StatsDB)
		self.StatsDB = self.Load(_db)
		_db.close()

		if 'Players' not in list(self.StatsDB.keys()):
			self.StatsDB['Players'] = {}

	def Load(self, _db):
		x = {}
		for key in list(_db.keys()):
			x[key] = _db[key]
		for k in ('GlobalWins', 'totalWins', 'totalPlayers'):
			if k not in x:
				x[k] = 0
		logger.info("Loaded stats database.")
		return x

	def Save(self):
		try:
			_db = shelve.open(self._StatsDB)
			for key in list(self.StatsDB.keys()):
				_db[key] = self.StatsDB[key]
			_db.close()
			logger.info("Saving stats database")
		except Exception as e:
			logger.exception("Error saving.")

	def AddStats(self, Player=None, Stat=None, Value=None):
		'''
		Check if we are adding stats to a player.
		If we are not, we fall back to globals.
		'''
		if Player:
			if Player not in list(self.StatsDB['Players'].keys()):
				self.StatsDB['Players'][Player] = {'overMax':0
					,'underMin':0
					,'tooHigh':0
					,'tooLow':0
					,'wins':0
					}
			self.StatsDB['Players'][Player][Stat] += Value
		else:
			if not self.StatsDB[Stat]:
				self.StatsDB[Stat] = Value
			else:
				self.StatsDB[Stat] += Value
		self.Save()

	def GetStatsPlayer(self, Person):
		st = self.StatsDB['Players'][Person]

		x = "\x02[Guess]\x02 Stats for {0}: {1} Guess(es) over max, {2} Guess(es) under min, {3} Guess(es) too high, {4} Guess(es) too low, and {5} win(s)."
		x = x.format(Person, st['overMax'], st['underMin'], st['tooHigh'], st['tooLow'], st['wins'])
		return x

	def GetStatsGlobal(self):
		p = [[None, 0]]
		for player in self.StatsDB['Players']:
			if self.StatsDB['Players'][player]['wins'] > p[0][1]:
				p[0][0] = player
				p[0][1] = self.StatsDB['Players'][player]['wins']
				del p[1:]
			elif self.StatsDB['Players'][player]['wins'] == p[0][1]:
				p.append([player, self.StatsDB['Players'][player]['wins']])
			else:
				pass

		if len(p) == 1:
			x = "\x02[Guess]\x02 There have been {0} global win{1}, among {2} total players, with {3} having the most wins of {4}."
			x = x.format(self.StatsDB['GlobalWins'], 's' if len(self.StatsDB['GlobalWins']) > 1 or self.StatsDB['GlobalWins'] == 0 else '', \
				len(self.StatsDB['Players']), p[0], p[1])
		else:
			x = "\x02[Guess]\x02 There have been {0} global win{1}, among {2} total players, with the players {3} tied at {4} wins."
			x = x.format(self.StatsDB['GlobalWins'], 's' if len(self.StatsDB['GlobalWins']) > 1 or self.StatsDB['GlobalWins'] == 0 else '', \
				len(self.StatsDB['Players']), ", ".join(x[0] for x in p), p[0][1])
		return x

class GuessingGame(object):
	def __init__(self):
		self.MaxNum = Settings.get("MaxNum", 250)
		self.CurrentNumber = None
		self.GenNumber()
		self._stats = Settings.get("UseStats", False)
		if self._stats:
			try:
				self.Stats = GuessingStats()
				logger.info("Enabling stats.")
			except Exception as e:
				logger.exception("Stats enable error.")

	def GenNumber(self, location=None):
		self.CurrentNumber = randint(1, self.MaxNum)
		if location:
			self.IRC.say(location, "Generating new number. Pick from 0-{0}".format(self.MaxNum))

	def SetMaxNum(self, data):
		try:
			self.MaxNum = int(data[4])
			self.GenNumber(data[2])
		except Exception:
			self.IRC.say(data[2], "I'm sorry {0}, but {1} doesn't seem to be a valid number.".format(data[0].split('!')[0], data[4]))

	def CheckGuess(self, data):
		UserGuess = int(data[4])
		if UserGuess > self.MaxNum:
			self.IRC.say(data[2], "I'm sorry {0}, but my maximum number is set to {1}.".format(data[0].split('!')[0], self.MaxNum))
			if self._stats:
				self.Stats.AddStats(Player=data[0].split('!')[0], Stat='overMax', Value=1)

		elif UserGuess <= 0:
			self.IRC.say(data[2], "I'm sorry {0}, but my number cannot be lower than 0.".format(data[0].split('!')[0]))
			if self._stats:
				self.Stats.AddStats(Player=data[0].split('!')[0], Stat='underMin', Value=1)

		elif UserGuess > self.CurrentNumber:
			self.IRC.say(data[2], "I'm sorry {0}, but my number is lower than that.".format(data[0].split('!')[0]))
			if self._stats:
				self.Stats.AddStats(Player=data[0].split('!')[0], Stat='tooHigh', Value=1)

		elif UserGuess < self.CurrentNumber:
			self.IRC.say(data[2], "I'm sorry {0}, but my number is higher than that.".format(data[0].split('!')[0]))
			if self._stats:
				self.Stats.AddStats(Player=data[0].split('!')[0], Stat='tooLow', Value=1)

		elif UserGuess == self.CurrentNumber:
			self.IRC.say(data[2], "Congratulations {0}, You guessed my number!".format(data[0].split('!')[0]))
			self.GenNumber(location=data[2])
			if self._stats:
				self.Stats.AddStats(Player=data[0].split('!')[0], Stat='wins', Value=1)
				self.Stats.AddStats(Stat='GlobalWins', Value=1)
		else:
			pass #Wut.

	def GetStat(self, data):
		if self._stats:
			if data[4]:
				x = data[4]
			try:
				self.IRC.say(data[2], self.Stats.GetStatsPlayer(x if x else data[0].split('!')[0]))
			except Exception:
				self.IRC.say(data[2], "I'm sorry {0}, but I couldn't find anything for '{1}'".format(data[0].split('!')[0], x if x else data[0].split('!')[0]))
		else:
			self.IRC.say(data[2], "Stats are not enabled.")

	def GetGlobalStat(self, data):
		if self._stats:
			self.IRC.say(data[2], self.Stats.GetStatsGlobal())
		else:
			self.IRC.say(data[2], "Stats are not enabled.")

class Main(GuessingGame):
	def __init__(self, Name, Parser):
		GuessingGame.__init__(self)
		self.__name__ = Name
		self.Parser = Parser
		self.IRC = self.Parser.IRC


	def Load(self):
		self.Parser.hookCommand("PRIVMSG", self.__name__, {"^@guess \d{1,}$": self.CheckGuess
			,"^@setguess \d{1,}$": self.SetMaxNum
			,"^@checkstats": self.GetStat
			,"^@globalstats": self.GetGlobalStat}
		)

	def Unload(self):
		pass
	def Reload(self):
		pass

