#!/usr/bin/python2
import requests
def get_slogan(text):
	r = requests.post('http://www.sloganmaker.com/sloganmaker.php', data={'user':text})
	if r.status_code == 200:
		return "\x02[SloganMaker]\x02 {0}".format(r.content.split('<p>')[1].split('</p>')[0])
	else:
		print("* [SloganMaker] Error - Status Code {0}".format(r.status_code))
		return "\x02[SloganMaker]\x02 Error; Status Code {0}".format(r.status_code)
		
