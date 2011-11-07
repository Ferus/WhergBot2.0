#!/usr/bin/python2
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
