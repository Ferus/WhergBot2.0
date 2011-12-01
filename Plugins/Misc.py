#!/usr/bin/python2
'''This module will contain misc commands so they are not scattered around.'''
from threading import Timer
from random import randint

def Act(msg, sock):
	sock.send("PRIVMSG {0} :\x01ACTION {1}\x01".format(msg[3], " ".join(msg[4].split()[1:])))
	
def Oven(msg, sock):
	location = msg[3]
	person = " ".join(msg[4].split()[1:])
	sock.send("PRIVMSG {0} :\x01ACTION prepares his ovens\x01".format(location))
	t = Timer(randint(7,11), sock.send, ("PRIVMSG {0} :\x01ACTION ovens {1}\x01".format(location, person), ))
	t.daemon = True
	t.start()
		
def Next(msg, sock):
	sock.say(msg[3], "Another satisfied customer! Next!")
		
def Bacon(msg, sock):
	person = " ".join(msg[4].split()[1:])
	if person == '':
		person = 'Ferus'
	sock.send("PRIVMSG {0} :\x01ACTION cooks up some fancy bacon for {1}\x01".format(location, person))
		
def AllowHug(msg, sock):
	sock.say(msg[3], "\x01ACTION hugs {0}.\x01".format(msg[0]))
def DenyHug(msg, sock):
	sock.say(msg[3], "\x01ACTION kicks {0} in the balls for not being a man.\x01".format(msg[0]))
	
def Echo(msg, sock):
	sock.say(msg[3], msg[4][6:])

def Raw(msg, sock):
	sock.send(msg[4][5:])
	
hooks = {
	'^@oven': [Oven, 5, False],
	'^@next': [Next, 5, False],
	'^@bacon': [Bacon, 5, False],
	'^@act': [Act, 5, False],
	';[_-]{1,};': [AllowHug, 4, False],
	';[_-]{1,};': [DenyHug, 5, False],
	'^@echo': [Echo, 4, False],
	'^\$raw': [Raw, 0, True],
	}
