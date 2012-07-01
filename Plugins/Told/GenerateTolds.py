#!/usr/bin/env python
import re
import requests


def GenCash4Tolds():
	y = int(x)
	while y != 0:
		r = requests.get('http://cash4told.com/')
		if r.status_code != 200:
			continue
		t = re.search("<span class=\"told\">(.*?)</span>", r.content.replace('\r', '').replace('\n', '').replace('\t', ''))
		t = t.groups()[0].strip()
		if t not in AllTolds:
			print(t)
			Tolds.write(t+"\n")
			AllTolds.append(t)
		else:
			pass
		y -= 1

def GenTheVoidTolds():
	y = int(x)
	while y != 0:
		r = requests.get('http://told.thevoid.no/')
		if r.status_code != 200:
			continue
		t = re.search("<body>(.*?)</body>", r.content.replace('\r', '').replace('\n', '').replace('\t', ''))
		t = t.groups()[0].strip()
		if t not in AllTolds:
			print(t)
			Tolds.write(t+'\n')
			AllTolds.append(t)
		else:
			pass
		y -= 1

if __name__ == '__main__':
	x = 100 #Number of times to request tolds.
	
	with open('Told.txt', 'r') as _t:
		AllTolds = _t.read().splitlines()
	
	Tolds = open('Told.txt', 'a')
	
#	GenCash4Tolds()
	GenTheVoidTolds()

	Tolds.close()
