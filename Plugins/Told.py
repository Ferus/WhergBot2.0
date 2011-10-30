#!/usr/bin/python2
from random import choice

class Told(object):
	def __init__(self, ToldFile=None, Socket=None):
		if ToldFile:
			with open(ToldFile, "r") as Tolds:
				self.ToldList = Tolds.readlines()
		if Socket:
			self.sock = Socket
	
	def ReturnTold(self, msg):
		 self.sock.send("PRIVMSG {0} :{1}".format(msg[3], choice(self.ToldList)))
