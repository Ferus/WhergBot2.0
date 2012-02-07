#!/usr/bin/env python
import requests
from CommandLock import Locker
Locker = Locker(5)

def get_slogan(text):
	r = requests.post('http://www.sloganmaker.com/sloganmaker.php', data={'user':text})
	if r.status_code == 200:
		return "\x02[SloganMaker]\x02 {0}".format(r.content.split('<p>')[1].split('</p>')[0])
	else:
		print("* [SloganMaker] Error - Status Code {0}".format(r.status_code))
		return "\x02[SloganMaker]\x02 Error; Status Code {0}".format(r.status_code)

def Slogan(msg, sock, users, allowed):
	try:
		if not Locker.Locked:
			sock.say(msg[3], get_slogan(" ".join(msg[4].split()[1:])))
			Locker.Lock()
		else:
			sock.notice(msg[0], "Please wait a little longer before using this command again")
	except Exception, e:
		print("* [SloganMaker] Error:\n* [SloganMaker] {0}".format(str(e)))

hooks = {
	'^@slogan': [Slogan, 5, False],
		}

helpstring = "@slogan <string> returns a 'slogan' from SloganMaker.com"
