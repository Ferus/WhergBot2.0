#!/usr/bin/env python
# Russian Roulette plugin.

# Credits to Buggles, MaoZedongs, and xqks of 
# irc.datnode.net for helping me create a list
# of guns and their chamber size. <3
# <&Eutectic> Ferus: make a random event where the person misses himself and randomly shoots somebody in the channel, preferably someone who was playing roulette
import random
from .Settings import Settings


def windex(lst):
	# Stolen from http://code.activestate.com/recipes/117241/
	'''an attempt to make a random.choose() function that makes weighted choices
	accepts a list of tuples with the item and probability as a pair'''
	wtotal = sum([x[1] for x in lst])
	n = random.uniform(0, wtotal)
	for item, weight in lst:
		if n < weight:
			break
		n = n - weight
	return item

class Main(object):
	def __init__(self, Name, Parser):
		self.__name__ = Name
		self.Parser = Parser
		self.IRC = self.Parser.IRC
		self.gunlist = Settings.get('guns')
		self.reasons = Settings.get('reasons')

	def Load(self):
		self.Parser.hookCommand('PRIVMSG', "^@roulette$", self.shoot)
		self.Parser.hookPlugin(self.__name__, Settings, self.Load, self.Unload, self.Reload)
	def Unload(self):
		pass
	def Reload(self):
		pass

	def init_gun(self, data):
		g = random.choice(self.gunlist)
		self.gun = g[0]
		self.chambers = [False] * g[1]
		self.bullets = 0
		self.IRC.say(data[2], "Loaded a {0} with {1} 'chambers'".format(self.gun, len(self.chambers)))
		self.load()
		
	def load(self):
		# increment bullet count by one
		for x in range(0, len(self.chambers)):
			if all(self.chambers):
				# cant add a bullet if the chambers are full
				break
			if self.chambers[x]:
				# pass a loaded chamber
				continue
			else:
				# replace an empty chamber with a bullet
				self.chambers[x] = not self.chambers[x]
				self.bullets += 1
				break
		random.shuffle(self.chambers)
	
	def shoot(self, data):
		if not hasattr(self, "gun"):
			self.init_gun(data)
		if self.chambers[0] == True:
			if windex([(True, .10), (False, .90)]):
				# 10% chance it's a dud
				self.bullets -= 1
				self.chambers[0] = False
				self.IRC.say(data[2], "You sigh once you realize the shot was a dud!")
			else:
				if windex([(True, .05), (False, .95)]):
					# 5% chance it backfires
					self.bullets -= 1
					self.chambers[0] = False
					self.IRC.say(data[2], "The {0} backfired! Sadly, you're still alive, but have suffered disfiguring scars.".format(self.gun))
				else:
					# an unlucky fate.
					r = random.choice(self.reasons).format(gun=self.gun)
					r += " \x02({0}/{1})\x02".format(self.bullets, len(self.chambers))
					if data[2] in Settings['killchans'] and hasattr(self.IRC, "kill"):
						self.IRC.kill(data[0].split("!")[0], r + " [{0}]".format(data[2]))
					else:
						self.IRC.banByMask(data[2], data[0])
						self.IRC.kick(data[2], data[0].split("!")[0], r)
					self.reset(data)
		else:
			# no bullet, add one and spin.
			self.IRC.say(data[2], "\x02*\x02click\x02*\x02")
			self.load()

	def reset(self, data):
		del self.gun
		del self.bullets
		del self.chambers
		self.init_gun(data)

