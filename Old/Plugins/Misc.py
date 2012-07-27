#!/usr/bin/env python
'''This module will contain misc commands so they are not scattered around.'''
from threading import Timer
from random import randint
import requests, re

def Act(msg, sock, users, allowed):
	x =  " ".join(msg[4].split()[1:])
	if not x:
		sock.action(msg[3], "slaps {0} upside the head".format(msg[0]))
	else:
		sock.action(msg[3], x)

def Oven(msg, sock, users, allowed):
	person = " ".join(msg[4].split()[1:])
	sock.action(msg[3], "prepares his ovens")
	t = Timer(randint(7,11), sock.action, (msg[3], "ovens {0}".format(person)))
	t.daemon = True
	t.start()

def Next(msg, sock, users, allowed):
	sock.say(msg[3], "Another satisfied customer! Next!")

def Bacon(msg, sock, users, allowed):
	person = " ".join(msg[4].split()[1:])
	if person == '':
		person = 'Ferus'
	sock.action(msg[3], "cooks up some fancy bacon for {0}".format(person))

def Hug(msg, sock, users, allowed):
	access = allowed.levelCheck(msg[0])[1][1]
	if access <= 4:
		sock.action(msg[3], "hugs {0}.".format(msg[0]))
	else:
		sock.action(msg[3], "kicks {0} in the balls for not being a man.".format(msg[0]))

def Echo(msg, sock, users, allowed):
	sock.say(msg[3], msg[4][6:])

def Raw(msg, sock, users, allowed):
	sock.send(msg[4][5:])

def isup(msg, sock, users, allowed):
	site = msg[4].split()[1]
	html = requests.get("http://www.isup.me/{0}".format(site))
	if html.status_code != 200:
		sock.say(msg[3], "I couldn't connect to isup.me.")
		return None
	html = re.sub("\t|\n", "", html.content)
	h = re.findall("<div id=\"container\">(.*?)<p>.*?</div>", html)[0]
	h = re.sub("<a href=\".*?\" class=\"domain\">", "", h)
	h = re.sub("</a>(:?</span>)?", "", h)
	h = re.sub("\s{2,}", " ", h).strip(" ")
	sock.say(msg[3], "\x02[ISUP]\x02 {0}".format(h))

hooks = {
	'^@oven': [Oven, 5, False],
	'^@next': [Next, 5, False],
	'^@bacon': [Bacon, 5, False],
	'^@act': [Act, 5, False],
	';[_-]{1,};': [Hug, 5, False],
	'^@echo': [Echo, 4, False],
	'^\$raw': [Raw, 0, True],
	'^@isup': [isup, 5, False],
	}

helpstring = """Holds a bunch of misc plugins;
@oven <object>: `Ovens` a person/thing.
@next: Another satisfied customer! Next! (Stolen from #Archlinux on freenode <3)
@bacon <object>: Cooks cyberbacon for a person/thing.
@act <thing to do>: Performs a /me command.
@echo <something>: Performs a /say commans. Simply echoing text.
@isup <site url>: Polls isup.me.
$raw <string>: Sends a raw string to the server. It's wise to limit this command.
A regex for crying emoticon faces is also included, if a user has access, s/he is hugged. :3"""
