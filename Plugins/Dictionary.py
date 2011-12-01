#!/usr/bin/python2

def h(msg, sock, users, allowed):
	sock.say(msg[3], "This command isnt implemented yet faggots.")

hooks = {
	'^@def': [h, 5, False],	
		}
