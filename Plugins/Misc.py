#!/usr/bin/python2
'''This module will contain misc commands so they are not scattered around.'''
from threading import Timer
from random import randint

class misc():
	def __init__(self, sock=None):
		if sock:
			self.sock = sock
		
	def Oven(self, location, person):
		self.sock.send("PRIVMSG {0} :\x01ACTION prepares his ovens\x01".format(location))
		t = Timer(randint(9,11), self.sock.send, ("PRIVMSG {0} :\x01ACTION ovens {1}\x01".format(location, person), ))
		t.daemon = True
		t.start()
		
	def Next(self, location):
		self.sock.say(location, "Another satisfied customer! Next!")
		
	def Bacon(self, location, person):
		if person == '':
			person = 'Ferus'
		self.sock.send("PRIVMSG {0} :\x01ACTION cooks up some fancy bacon for {1}\x01".format(location, person))
