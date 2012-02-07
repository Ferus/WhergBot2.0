#!/usr/bin/env python
from random import choice

class Told(object):
	def __init__(self, ToldFile=None):
		if ToldFile:
			with open(ToldFile, "r") as Tolds:
				self.ToldList = Tolds.readlines()

	def ReturnTold(self, msg, sock, users, allowed):
		 sock.say(msg[3], choice(self.ToldList))

t = Told("Plugins/Told.txt")
hooks = {
	'^@told': [t.ReturnTold, 5, False],
		}

helpstring = "@told: Sends a random 'Told' string"
