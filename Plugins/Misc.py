#!/usr/bin/python2
'''This module will contain misc commands so they are not scattered around.'''
from threading import Timer
from random import randint

class misc():
	def Act(self, msg, sock):
		sock.send("PRIVMSG {0} :\x01ACTION {1}\x01".format(msg[3], " ".join(msg[4].split()[1:])))
		
	def Oven(self, msg, sock):
		location = msg[3]
		person = " ".join(msg[4].split()[1:])
		sock.send("PRIVMSG {0} :\x01ACTION prepares his ovens\x01".format(location))
		t = Timer(randint(7,11), sock.send, ("PRIVMSG {0} :\x01ACTION ovens {1}\x01".format(location, person), ))
		t.daemon = True
		t.start()
		
	def Next(self, msg, sock):
		sock.say(msg[3], "Another satisfied customer! Next!")
		
	def Bacon(self, msg, sock):
		person = " ".join(msg[4].split()[1:])
		if person == '':
			person = 'Ferus'
		sock.send("PRIVMSG {0} :\x01ACTION cooks up some fancy bacon for {1}\x01".format(location, person))
		
	def AllowHug(self, msg, sock):
		sock.say(msg[3], "\x01ACTION hugs {0}.\x01".format(msg[0]))
	def DenyHug(self, msg, sock):
		sock.say(msg[3], "\x01ACTION kicks {0} in the balls for not being a man.\x01".format(msg[0]))
		
	def Echo(self, msg, sock):
		try:
			sock.say(msg[3], msg[4][6:])
		except Exception, e:
			print("* [Echo] Error")
			print(e)

	def Raw(self, msg, sock):
		'''Send a raw message to the IRC server.'''
		try:
			sock.send(msg[4][5:])
		except Exception, e:
			print("* [Raw] Error")
			print(e)
	
M = misc()
hooks = {
	'^@oven': [M.Oven, 5, False],
	'^@next': [M.Next, 5, False],
	'^@bacon': [M.Bacon, 5, False],
	'^@act': [M.Act, 5, False],
	';[_-]{1,};': [M.AllowHug, 4, False],
	';[_-]{1,};': [M.DenyHug, 5, False],
	'^@echo': [M.Echo, 4, False],
	'^\$raw': [M.Raw, 0, True],
	}
