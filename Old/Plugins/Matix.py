#!/usr/bin/env python
import os
from random import choice

class Matix(object):
	def __init__(self):
		self.Files = os.listdir("Spams")

	def Matix(self, Msg, Sock, Users, Allowed):
		tmp = Msg[4].split()[1:]
		if tmp[0] == 'list':
			self.SendList(Msg[0], Sock)

		elif tmp[0] == 'random':
			x = choice(self.Files)
			with open("Spams/{0}".format(x)) as _f:
				for line in _f.readlines():
					Sock.say(Msg[3], line)
		elif tmp[0] in self.Files:
			with open("Spams/{0}".format(tmp[0])) as _f:
				for line in _f.readlines():
					Sock.say(Msg[3], line)
		else:
			self.SendList(Msg[0], Sock)

	def SendList(self, Person, Sock):
		f = list(self.Files)
		for i in xrange(0, len(f), 10):
			Sock.send("NOTICE {0} :{1}".format(Person, "  ".join(f[i:i+8]) ))
M = Matix()

hooks = {
	"^@matix": [M.Matix, 0, True],
	}

helpstring = """Spams ascii art from the Spams folder. Do NOT use this without '/os flood'
@matix random: Chooses a random file.
@matix <filename.txt>: Spams a specific filename.
@matix list: Lists all files in the Spams folder."""
