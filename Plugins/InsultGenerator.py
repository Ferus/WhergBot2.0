#!/usr/bin/env python
# InsultGenerator.py - Pulls an 'insult' from http://www.insultgenerator.org/

import requests
from htmldecode import convert

def insult():
	html = requests.get("http://www.insultgenerator.org/")
	if html.status_code != 200:
		return "I couldn't connect to http://insultgenerator.org/ faggot."
	html = convert(html.content)
	insult = html.split("<TR align=center><TD>")[1].split("</TD></TR>")[0]
	return insult
	
def gen(msg, sock, users, allowed):
	'''Insult a fgt. :)'''
	_insult = "{0}, {1}".format(" ".join(msg[4].split()[1:]), insult())
	sock.say(msg[3], _insult)
	
hooks = {
	'^@insult': [gen, 5, False],	
		}

helpstring = "Insults someone/something. Polls insultgenerator.org for an insult."
