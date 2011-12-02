#!/usr/bin/python2
class wordnikObj(object):
	def __init__(self, apiFile):
		try:
			from wordnik import Wordnik
			self._imported = True
		except ImportError:
			print("* [Dictionary] Could not import wordnik, please read the README and install it.")
			self._imported = False
			
		try:
			with open(apiFile, "r") as _f:
				api = _f.read().strip()
				print("* [Dictionary] Using API Key '{0}'".format(api))
		except:
			print("* [Dictionary] Could not find API Key File. Please place your API Key (alone) in a file.")

		if self._imported:
			self.Word = Wordnik(api_key=api)
		
	def reply(self, msg, sock, users, allowed):
		if self._imported:
			w = " ".join(msg[4].split()[1:])
			defs = []
			deflist = self.Word.word_get_definitions(w)[0:3]
			numdefs = len(deflist)

			for x in deflist:
				defs.append(x['text'])
					
			if numdefs == 0:
				sock.say(msg[3], "I didn't find any definitions for '{0}'.".format(w))
			elif numdefs == 1:
				sock.say(msg[3], "I found one definition for '{0}'.".format(w))
				sock.say(msg[3], "\x01{0}\x01: {1}".format(w, defs[0]))
			else:
				sock.say(msg[3], "I found {0} definitions for '{1}'.".format(numdefs, w))
				while len(defs) != 0:
					sock.say(msg[3], "\x01{0}\x01: {1}".format(w, defs.pop(0)))
		else:
			sock.say(msg[3], "Please install the python wordnik API and get a developers API key. http://developer.wordnik.com/libraries#python")

W = wordnikObj("Plugins/DictionaryAPIKey.txt")

hooks = {
	'^@def': [W.reply, 5, False],	
		}
