#!/usr/bin/python2

from random import randint
import shelve

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
	#The most people who have played at once
	A function that gets absolute totals of all players' stats.
	
	{
	'Players': {
		'Ferus': {
			'notValid':0,
			'overMax':0, },

		'ExamplePerson': {
			'notValid':0,
			'overMax':0, },
		#End Players Block },
	
	#Globals
	'totalWins':0,
	'totalPlayers':len(db['Players'])
	}
	#Etc
	'''
	
	def __init__(self, _StatsDB=None):		
		if _StatsDB:
			self._StatsDB = _StatsDB
		else:
			self._StatsDB = "Plugins/GuessingGameStats.shelve"

		_db = shelve.open(self._StatsDB)
		self.StatsDB = self.Load(_db)
		_db.close()

		if 'Players' not in self.StatsDB.keys():
			self.StatsDB['Players'] = {}
				
	def Load(self, _db):
		x = {}
		for key in _db.keys():
			x[key] = _db[key]
		print("* [Guess] Loaded stats database.")
		return x
		
	def Save(self):
		try:
			_db = shelve.open(self._StatsDB)
			for key in self.StatsDB.keys():
				_db[key] = self.StatsDB[key]
			_db.close()
			print("* [Guess] Saving stats database")
			return True
		except Exception, e:
			print(repr(e))
			return False
			
	def AddStats(self, Player=None, Stat=None, Value=None):
		'''
		Check if we are adding stats to a player.
		If we are not, we fall back to globals.
		'''
		try:
			if Player:
				if Player not in self.StatsDB['Players'].keys():
					self.StatsDB['Players'][Player] = {
						'notValid':0,
						'overMax':0,
						'underMin':0,
						'tooHigh':0,
						'tooLow':0,
						'wins':0,
						}
						
				self.StatsDB['Players'][Player][Stat] += Value

			else:
				if not self.StatsDB[Stat]:
					self.StatsDB[Stat] = Value
				else:
					self.StatsDB[Stat] += Value
			self.Save()
		except:
			print("* [Guess] Error'd")

	def GetStats(self, Person):
		st = self.StatsDB['Players'][Person]
				
		x = "\x02[Guess]\x02 Stats for {0}: {1} Non-valid number(s), {2} Guess(es) over max, {3} Guess(es) under min, {4} Guess(es) too high, {5} Guess(es) too low, and {6} win(s)."
		x = x.format(Person, st['notValid'], st['overMax'], st['underMin'], st['tooHigh'], st['tooLow'], st['wins'])
		return x			
		
class GuessingGame(object):
	def __init__(self, _stats=False):
		self.MaxNum = 250
		self.CurrentNumber = None
		self.GenNumber()

		self._stats = _stats
		if self._stats:
			print("* [Guess] Enabling stats.")
			self.Stats = GuessingStats()

	def GenNumber(self, sock=None, location=None):
		self.CurrentNumber = randint(1, self.MaxNum)
		if sock and location:
			sock.say(location, "Generating new number. Pick from 0-{0}".format(self.MaxNum))

	def SetMaxNum(self, msg, sock, users, allowed):
		try:
			ToSet = int(msg[4].split()[1])
			self.MaxNum = ToSet
			self.GenNumber(sock=sock, location=msg[3])
		except:
			sock.say(msg[3], "I'm sorry {0}, but {1} doesn't seem to be a valid number.".format(msg[0], msg[4].split()[1]))
			
	def CheckGuess(self, msg, sock, users, allowed):
		try:
			UserGuess = int(msg[4].split()[1])
		except:
			sock.say(msg[3], "I'm sorry {0}, but {1} doesn't seem to be a valid number.".format(msg[0], msg[4].split()[1]))
			if self._stats:
				self.Stats.AddStats(Player=msg[0], Stat='notValid', Value=1)
			return None

		if UserGuess > self.MaxNum:
			sock.say(msg[3], "I'm sorry {0}, but my maximum number is set to {1}.".format(msg[0], self.MaxNum))
			if self._stats:
				self.Stats.AddStats(Player=msg[0], Stat='overMax', Value=1)
				
		elif UserGuess <= 0:
			sock.say(msg[3], "I'm sorry {0}, but my number cannot be lower than 0.".format(msg[0]))
			if self._stats:
				self.Stats.AddStats(Player=msg[0], Stat='underMin', Value=1)
				
		elif UserGuess > self.CurrentNumber:
			sock.say(msg[3], "I'm sorry {0}, but my number is lower than that.".format(msg[0]))
			if self._stats:
				self.Stats.AddStats(Player=msg[0], Stat='tooHigh', Value=1)
				
		elif UserGuess < self.CurrentNumber:
			sock.say(msg[3], "I'm sorry {0}, but my number is higher than that.".format(msg[0]))
			if self._stats:
				self.Stats.AddStats(Player=msg[0], Stat='tooLow', Value=1)
				
		elif UserGuess == self.CurrentNumber:
			sock.say(msg[3], "Congratulations {0}, You guessed my number!".format(msg[0]))
			self.GenNumber(sock=sock, location=msg[3])
			if self._stats:
				self.Stats.AddStats(Player=msg[0], Stat='wins', Value=1)
		else:
			pass #Wut.

	def GetStat(self, msg, sock, users, allowed):
		try:
			sock.say(msg[3], self.Stats.GetStats(msg[0]))
		except:
			sock.say(msg[3], "I'm sorry {0}, but I couldn't find any stats for you.".format(msg[0]))
			
G = GuessingGame(_stats=True)

hooks = {
	'^@guess': [G.CheckGuess, 5, False],
	'^@setguess': [G.SetMaxNum, 3, False],
	'^@checkstats': [G.GetStat, 5, False],
	}
