#!/usr/bin/python2
from random import choice

class Told(object):
	def __init__(self, ToldFile=None):
		if ToldFile:
			with open(ToldFile, "r") as Tolds:
				self.ToldList = Tolds.readlines()
	
	def ReturnTold(self, msg, sock, users, allowed):
		 sock.send("PRIVMSG {0} :{1}".format(msg[3], choice(self.ToldList)))

t = Told("Plugins/Told.txt")
hooks = {
	'^@told': [t.ReturnTold, 5, False],	
		}
