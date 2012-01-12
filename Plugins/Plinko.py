#!/usr/bin/python2
import random
import re
from threading import Timer

class Plinko(object):
	def __init__(self):
		'''
		Challenged to write a plinko plugin.
		A great game from The Price Is Right.
		However, I'm fairly sure this will be pretty spammy.
		'''
		random.seed(__import__("os").urandom(30))
		self.Head = "|_._._._._._._._._|"
		self.Tail = "|._._._._._._._._.|"
		self.End = "|_|_|_|_|_|_|_|_|_|"
		self.isHead = True
		self.Location = None
		self.Locked = False
		
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
			
	def Lock(self):
		if not self.Locked:
			self.Locked = True
			t = Timer(5, self.UnLock, ())
			t.daemon = True
			t.start()
	def UnLock(self):
		self.Locked = False

	def Start(self, StartLocation):
		if type(StartLocation) != int:
			return None
		if StartLocation not in range(1,10):
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

Pl = Plinko()

def Parse(Msg, Sock, Users, Allowed):
	if Msg[3] not in chans:
		Sock.notice(Msg[0], "Go back to #games faggot.")
		return None
	if Pl.Locked:
		Sock.notice(Msg[0], "Locked. Try again in a few seconds.")
		return None
	try:
		x = int(Msg[4].split()[1])
		if x > 9:
			Sock.say(Msg[3], '\x02[Plinko]\x02 Error: Number too large, defaulting to 5.')
			x = 5
		elif x < 1:
			Sock.say(Msg[3], '\x02[Plinko]\x02 Error: Number too small, defaulting to 5.')
			x = 5
		else:
			pass
	except:
		Sock.say(Msg[3], '\x02[Plinko]\x02 Error: Defaulting to 5.')
		x = 5
	for line in Pl.Start(x):
		Sock.say(Msg[3], line)
	Pl.Lock()
	try:
		for x in prizes[str(Pl.Location)]:
			exec(x)
	except Exception, e:
		Sock.say(Msg[3], "\x02[Plinko]\x02 Error: {0}".format(str(repr(e))))
		
hooks = {
	"^@plinko": [Parse, 5, False],
	}

helpstring = """An ascii version of Plinko from The Price Is Right.
@plinko <number>: If a number is specified, it will start in that slot. Defaults to 5"""

chans = ['#games']

prizes = {
	'1' : ["Sock.say(Msg[3], '{0}'.format(random.choice(phrases)))"],
	'2' : ["Sock.say(Msg[3], '{0}'.format(random.choice(phrases)))"],
	'3' : ["Sock.say(Msg[3], '{0}'.format(random.choice(phrases)))"],
	'4' : ["Sock.say(Msg[3], '!tkb {0} 2m You fucking suck.'.format(Msg[0]))", "t = Timer(125, Sock.invite, (Msg[0], Msg[3],))", "t.daemon = True", "t.start()"],
	'5' : ["Sock.say(Msg[3], '!access add {0} 5'.format(Msg[0]))", "t = Timer(300, Sock.say, (Msg[3], '!access del {0}'.format(Msg[0]),))", "t.daemon = True", "t.start()"],
	'6' : ["Sock.say(Msg[3], '!tkb {0} 2m You fucking suck.'.format(Msg[0]))", "t = Timer(125, Sock.invite, (Msg[0], Msg[3],))", "t.daemon = True", "t.start()"],
	'7' : ["Sock.say(Msg[3], '{0}'.format(random.choice(phrases)))"],
	'8' : ["Sock.say(Msg[3], '{0}'.format(random.choice(phrases)))"],
	'9' : ["Sock.say(Msg[3], '{0}'.format(random.choice(phrases)))"],
	}
phrases = [
	"YOU DIDN'T EVEN GET CLOSE, FAGGOT!",
	"Try again you fucking faggot.",
	"How about you stop sucking dicks and /TRY/ to win next time.",
	"Congratulations, you didn't win shit.",
	]
