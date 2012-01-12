#!/usr/bin/python2
import requests
'''
Poll automeme.net for a 'meme'.
Usage: import Meme, m = Meme.meme(), next(m)
'''
urls = {
	"regular": "http://api.automeme.net/text?lines=80",
	"hipster": "http://api.automeme.net/text?lines=80&vocab=hipster",
	}

def get_meme(t):
	'''
	Creates a generator to store memes in a list.
	t is the type of url to retrieve from
	'''
	meme_db = []
	memeurl = urls[t]
	try:
		memes = requests.get(memeurl).content.replace('_','\x02').split("\n")
	except:
		print("* [AutoMeme] Error requesting new memes.")
		return get_meme()
	for meme in memes:
		meme_db.append(meme)
	meme_db.pop()
	return meme_db
	
def meme(t):
	'''Returns a meme from the list'''
	meme_db = []
	while True:
		if not meme_db:
			print("* [AutoMeme] Getting moar memes!")
			meme_db = get_meme(t)
		memestr = meme_db[0]
		del meme_db[0]
		yield "\x02[AutoMeme]\x02 {0}".format(memestr)

RegularMeme = meme(t='regular')
HipsterMeme = meme(t='hipster')

def RegMeme(msg, sock, users, allowed):
	try:
		sock.say(msg[3], next(RegularMeme))
	except Exception, e:
		print("* [AutoMeme] Error:\n* [AutoMeme] {0}".format(str(e)))

def HipMeme(msg, sock, users, allowed):
	try:
		sock.say(msg[3], next(HipsterMeme))
	except Exception, e:
		print("* [AutoMeme] Error:\n* [AutoMeme] {0}".format(str(e)))

hooks = {
	'^@meme': [RegMeme, 5, False],
	'^@hipmeme': [HipMeme, 5, False],
		}

helpstring = """Polls automeme.net for some lulzy content.
@meme: A regular meme
@hipmeme: A hipster themed meme using automeme's `new` API."""
