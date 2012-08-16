#!/usr/bin/env python
import random
import re
from threading import Timer
from os import urandom
from Parser import Locker
from .Settings import Settings

Locker = Locker(0)

class Plinko(object):
	def __init__(self):
		'''
		Challenged to write a plinko plugin.
		A great game from The Price Is Right.
		However, I'm fairly sure this will be pretty spammy.
		'''
		random.seed(urandom(30))
		self.Head = "|_._._._._._._._._|"
		self.Tail = "|._._._._._._._._.|"
		self.End = "|_|_|_|_|_|_|_|_|_|"
		self.isHead = True
		self.Location = None

		self.GoLeftHead = {
			"1":"1", #Cant go left.
			"2":"1",
			"3":"2",
			"4":"3",
			"5":"4",
			"6":"5",
			"7":"6",
			"8":"7",
			"9":"8",
			}
		self.GoRightHead = {
			"1":"1",
			"2":"2",
			"3":"3",
			"4":"4",
			"5":"5",
			"6":"6",
			"7":"7",
			"8":"8",
			"9":"8", #Cant go right
			}
		self.GoLeftTail = {
			"1":"1",
			"2":"2",
			"3":"3",
			"4":"4",
			"5":"5",
			"6":"6",
			"7":"7",
			"8":"8",
			}
		self.GoRightTail = {
			"1":"2",
			"2":"3",
			"3":"4",
			"4":"5",
			"5":"6",
			"6":"7",
			"7":"8",
			"8":"9",
			}
	def Left(self, Pos):
		if self.isHead:
			self.Trigger()
			return int(self.GoLeftHead[Pos])
		else:
			self.Trigger()
			return int(self.GoLeftTail[Pos])
	def Right(self, Pos):
		if self.isHead:
			self.Trigger()
			return int(self.GoRightHead[Pos])
		else:
			self.Trigger()
			return int(self.GoRightTail[Pos])

	def ChooseDirection(self, Pos):
		if random.choice([True]*50 + [False]*50):
			return self.Left(Pos)
		else:
			return self.Right(Pos)

	def Replace(self, String, Location):
		x = 1
		s = ""
		for y in String:
			if y == "_":
				if x == Location:
					s += "o"
					x+=1
				else:
					s += "_"
					x+=1
			elif y == ".":
				s += "."
			else:
				s += "|"
		return s

	def Trigger(self):
		if self.isHead:
			self.isHead = False
		else:
			self.isHead = True

	def Start(self, StartLocation):
		if type(StartLocation) != int:
			return None
		if StartLocation not in list(range(1,10)):
			return None
		self.Location = StartLocation

		Game = []
		Game.append(self.Replace(self.Head, self.Location))
		for x in range(12):
			self.Location = self.ChooseDirection(str(self.Location))
			if self.isHead:
				x = self.Replace(self.Head, self.Location)
			else:
				x = self.Replace(self.Tail, self.Location)
			Game.append(x)
		Game.append(self.Replace(self.End, self.Location))
		return Game

class Main(object):
	def __init__(self, Name, Parser):
		self.__name__ = Name
		self.Parser = Parser
		self.IRC = self.Parser.IRC

		self.Plinko = Plinko()

	def Parse(self, data):
		if data[2] not in Settings.get('allowedchans'):
			self.IRC.say(data[2], "Plinko is not allowed in here.")
			return None
		if Locker.Locked:
			self.IRC.notice(data[0].split('!')[0], "Locked. Try again in a few seconds.")
			return None
		try:
			x = int(data[4])
			if x > 9:
				self.IRC.say(data[2], '\x02[Plinko]\x02 Error: Number too large, defaulting to 5.')
				x = 5
			elif x < 1:
				self.IRC.say(data[2], '\x02[Plinko]\x02 Error: Number too small, defaulting to 5.')
				x = 5
			else:
				pass
		except:
			self.IRC.say(data[2], '\x02[Plinko]\x02 Error: Defaulting to 5.')
			x = 5
		for line in self.Plinko.Start(x):
			self.IRC.say(data[2], line)
		Locker.Lock()
		try:
			for x in Settings.get('prizes')[str(self.Plinko.Location)]:
				exec(x)
		except Exception as e:
			self.IRC.say(data[2], "\x02[Plinko]\x02 Error: {0}".format(str(repr(e))))

	def Load(self):
		self.Parser.hookCommand('PRIVMSG', '^@plinko(?: \d{1})?$', self.Parse)
		self.Parser.hookPlugin(self.__name__, Settings, self.Load, self.Unload, self.Reload)

	def Unload(self):
		pass
	def Reload(self):
		pass



