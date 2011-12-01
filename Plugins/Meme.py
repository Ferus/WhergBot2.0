#!/usr/bin/python2
import requests
'''
Poll automeme.net for a 'meme'.
Usage: import Meme, m = Meme.meme(), next(m)
'''
		
def get_meme():
	'''Creates a generator to store memes in a list.'''
	meme_db = []
	memeurl = "http://api.automeme.net/text?lines=80"
	try:
		memes = requests.get(memeurl).content.replace('_','\x02').split("\n")
	except:
		print("* [AutoMeme] Error requesting new memes.")
		return get_meme() #This /should/ force it to call itself again if we cant connect.
	for meme in memes:
		meme_db.append(meme)
	meme_db.pop()
	return meme_db
	
def meme():
	'''Returns a meme from the list'''
	meme_db = []
	while True:
		if not meme_db:
			print("* [AutoMeme] Getting moar memes!")
			meme_db = get_meme()
		memestr = meme_db[0]
		del meme_db[0]
		yield "\x02[AutoMeme]\x02 {0}".format(memestr)

MemeGen = meme()
def MString(msg, sock, users, allowed):
	try:
		sock.say(msg[3], next(MemeGen))
	except Exception, e:
		print("* [AutoMeme] Error:\n* [AutoMeme] {0}".format(str(e)))

hooks = {
	'^@meme': [MString, 5, False],	
		}
	
	
	
	
	
