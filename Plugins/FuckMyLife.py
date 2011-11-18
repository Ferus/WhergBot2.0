#!/usr/bin/python2
import requests
import re

def get_fml():
	fml_db = []
	url = "http://fmylife.com/random"
	_html = requests.get(url)
	if _html.status_code != 200:
		return False #Error
	_html = _html.content #Page HTML
	comp = "<div class=\"post article\" id=\"[0-9]{1,}\"><p><a href=\"\/[a-zA-Z0-9_-]{1,}\/[0-9]{1,}\" class=\"fmllink\">.*?</a></p>"
	tmp = re.findall(comp, _html)
	for x in tmp:
		x = re.sub("<div class=\"post article\" id=\"[0-9]{1,}\"><p><a href=\"\/[a-zA-Z0-9_-]{1,}\/[0-9]{1,}\" class=\"fmllink\">", "", x)
		x = re.sub("</a><a href=\"\/[a-zA-Z0-9_-]{1,}\/[0-9]{1,}\" class=\"fmllink\">", "", x)
		x = re.sub("</a></p>", "", x)
		fml_db.append(x)
	return fml_db

def fml():
	fml_db = []
	while True:
		if not fml_db:
			print("* [FML] Getting more FML's.")
			fml_db = get_fml()
		_fml = fml_db.pop()
		yield "\x02[FML]\x02 {0}".format(_fml)

FmlGen = meme()
def FMLString(msg, sock):
	try:
		sock.say(msg[3], next(FmlGen))
	except Exception, e:
		print("* [FML] Error:\n* [FML] {0}".format(str(e)))

hooks = {
	'^@fml': [FMLString, 5, False],
	}
