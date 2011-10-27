#!/usr/bin/python2

import re

from Plugins import SloganMaker, UrbanDictionary, MpdScript, Misc, Stream, Meme, Quotes, Told, Tinyboard

class Commands():
	def __init__(self, nick=None, sock=None, parser=None, allowed=None):
		'''Here we define a dictionary of commands with access levels, and what to do if they are called.
		Each command receives the raw message in a list. Optional socket allows for raw IRC commands.
		
		Every function defined in here has to receive a 'msg' variable, which is a list returned from the parser. IE:
		['Ferus', 'anonymous@the.interwebs', 'PRIVMSG', '#hacking', '$quit Some quit message.', '$quit']
		msg[4][6:] == "Some quit message."
		'''
		self.cmdVar = "@"
		self.nick = nick
		
		self.sock = sock
		self.parser = parser
		self.allowed = allowed
		
		### PLUGIN OBJECTS
		self.M = Meme.meme()
		self.misc = Misc.misc(sock=self.sock)
		self.stream = Stream.Stream()
		self.IRCq = Quotes.IRCQuotes("./Plugins/Pickle_Quotes.pkl")
		self.IRCr = Quotes.IRCRules("./Plugins/IRCRules.txt")
		self.tolds = Told.Told("./Plugins/Told.txt", self.sock)
		self.chon = Tinyboard.TinyBoard()
			
			
		self.cmds = {
			# Command name to be called : Block of code to execute, Access level, Hostcheck
			# If you want to disable a command, just comment out the line for it.
			'echo': [self.Echo, 4, False],
			'raw': [self.Raw, 0, True],
			'names': [self.Names, 0, False],
			'join': [self.Join, 3, True],
			'part': [self.Part, 3, True],
			'quit': [self.Quit, 0, True],
			'access': [self.Access, 0, True],
			'act': [self.Act, 5, False],
			
			'meme': [self.Meme, 5, False],
			'slogan': [self.Slogan, 5, False],
			'ud': [self.UD, 5, False],
			'mpd': [self.Music, 1, True],
			'oven': [self.Oven, 5, False],
			'next': [self.Next, 5, False],
			'bacon': [self.Bacon, 5, False],
			'stream': [self.Stream, 5, False],
			'quote': [self.Quote, 5, False],
			'q': [self.Quote, 5, False],
			'qsearch': [self.QuoteSearch, 5, False],
			'qfind': [self.QuoteSearch, 5, False],
			'qcount': [self.QuoteCount, 5, False],
			'qadd': [self.QuoteAdd, 0, True],
			'qdel': [self.QuoteDel, 0, True],
			'qbackup': [self.QuoteBackup, 0, True],
			'r': [self.Rule, 5, False],
			'rule': [self.Rule, 5, False],
			'rrand': [self.RandRule, 5, False],
			'told': [self.tolds.ReturnTold, 5, False],
					}
					
		self.noVar_cmds = {
			'4chon.net': [self.TinyboardLink, 5, False],
			'gattsuchan.tk': [self.TinyboardLink, 5, False],
			';_;': [self.Hug, 5, False],
			';-;': [self.Hug, 5, False],
					}

	def Echo(self, msg):
		'''Echos a message back'''
		try:
			self.sock.say(msg[3], msg[4][6:])
		except Exception, e:
			print("* [Echo] Error")
			print(e)
			
	def Raw(self, msg):
		'''Send a raw message to the IRC server.'''
		try:
			self.sock.send(msg[4][5:])
		except Exception, e:
			print("* [Raw] Error")
			print(e)
			
	def Names(self, msg):
		'''Debugging for users in a channel.'''
		try:
			for key in self.parser.users.keys():
				print(key, self.parser.users[key])
				
		except Exception, e:
			print("* [Names] Error")
			print(e)
			
	def Join(self, msg):
		try:
			self.sock.join(msg[4][6:])
		except Exception, e:
			print("* [Join] Error")
			print(e)
			
	def Part(self, msg):
		try:
			if not msg[4][6:]:
				self.sock.part(msg[3])
				del self.parser.users[msg[3]]
			else:
				self.sock.part(msg[4][6:])
				del self.parser.users[msg[4][6:]]
		except Exception, e:
			print("* [Part] Error")
			print(e)
	
	def Quit(self, msg):
		if type(msg) == list:
			msg = msg[4][6:]
			if msg == '':
				msg = "Quitting!"
		elif type(msg) == str:
			msg = msg
			
		self.sock.quit(msg)
		print("* [IRC] Quitting with message '{0}'.".format(msg))
		self.allowed.save()
		print("* [Allowed] Saving database.")
		self.sock.close()
		print("* [IRC] Closing Socket.")
		quit()
	
	def Access(self, msg):
		Nick = msg[0]
		Host = msg[1]
		Action = msg[2]
		Location = msg[3]
		Text = msg[4]
	
		if self.allowed.db[Nick][1] == 0:
			try:
				levels = {0: self.allowed.addOwner, 1: self.allowed.addAdmin}
				tmp = Text.split()[1:]

				if tmp[0] == 'add':
					if tmp[2] == 'None':
						tmp[2] = None
					
					if tmp[1] == self.allowed.owner[0]:
						self.sock.say(Location, "You cannot change your access.")
						print("* [Access] Denied changing owners access.")
						return None
						
					if int(tmp[3]) in levels.keys():
						levels[int(tmp[3])](tmp[1], tmp[2])								
					else:
						self.allowed.addOther(tmp[1], tmp[2], int(tmp[3]))
						
					self.sock.say(Location, "{0}, {1} added at level {2}".format(tmp[1], tmp[2], tmp[3]))
					print("* [Access] {0}, {1} added at level {2}.".format(tmp[1], tmp[2], tmp[3]))
						
				elif tmp[0] == 'del':
					if self.allowed.levelCheck(tmp[1]):
						if tmp[1] != self.allowed.owner[0]:
							del self.allowed.db[tmp[1]]
							self.sock.say(Location, "Deleted access for {0}".format(tmp[1]))
							print("* [Access] Deleted access for {0}.".format(tmp[1]))
						else:
							self.sock.say(Location, "Access for {0} cannot be deleted.".format(tmp[1]))
					else:
						self.sock.say(Location, "No access level found for {0}".format(tmp[1]))
				
				elif tmp[0] == 'show':
					try:								
						self.sock.say(Location, str(self.allowed.db[tmp[1]]))
					except Exception, e:
						print(e)
						
				
			except Exception, e:
				self.sock.send("NOTICE {0} :{1}".format(Nick, "Format for 'access' is: `access add/del Nick Ident@host Level`"))
				print("* [Access] Error:\n* [Access] {0}".format(str(e)))
				
	def Act(self, msg):
		try:
			self.sock.send("PRIVMSG {0} :\x01ACTION {1}\x01".format(msg[3], " ".join(msg[4].split()[1:])))
		except Exception, e:
			print("* [Act] Error:\n* [Act] {0}".format(str(e)))
	
	
	### PLUGINS
	def Meme(self, msg):
		try:
			self.sock.say(msg[3], next(self.M))
		except Exception, e:
			print("* [AutoMeme] Error:\n* [AutoMeme] {0}".format(str(e)))
			
	def Slogan(self, msg):
		try:
			self.sock.say(msg[3], SloganMaker.get_slogan(" ".join(msg[4].split()[1:])))
		except Exception, e:
			print("* [SloganMaker] Error:\n* [SloganMaker] {0}".format(str(e)))
			
	def UD(self, msg):
		try:
			self.sock.say(msg[3], UrbanDictionary.request(" ".join(msg[4].split()[1:])))
		except Exception, e:
			print("* [UrbanDict] Error:\n* [UrbanDict] {0}".format(str(e)))
			
	def Music(self, msg):
		try:
			if msg[4].split()[1:]:
				Text = msg[4].split()[1:]
			else:
				Text = []
				
			if len(Text) < 1:
				self.sock.say(msg[3], MpdScript.mpdshow_cb())
			elif Text[0] == "next":
				self.sock.say(msg[3], MpdScript.mpdnext_cb())
			elif Text[0] == "prev":
				self.sock.say(msg[3], MpdScript.mpdprev_cb())
		except Exception, e:
			print("* [MPD] Error:\n* [MPD] {0}".format(str(e)))
	
	def Oven(self, msg):
		try:
			ovenee = " ".join(msg[4].split()[1:])
			self.misc.Oven(msg[3], ovenee)
		except Exception, e:
			print("* [Oven] Error:\n* [Oven] {0}".format(str(e)))
		
	def Next(self, msg):
		try:
			self.misc.Next(msg[3])
		except Exception, e:
			print("* [Next] Error:\n* [Next] {0}".format(str(e)))
			
	def Bacon(self, msg):
		try:
			person = " ".join(msg[4].split()[1:])
			self.misc.Bacon(msg[3], person)
		except Exception, e:
			print("* [Bacon] Error:\n* [Bacon] {0}".format(str(e)))
	
	def Stream(self, msg):
		try:
			if msg[4].split()[1:]:
				Text = msg[4].split()[1:]
			else:
				Text = []
			
			if Text[0] == 'np' or Text[0].lower() == 'now' and Text[1].lower() == 'playing':
				self.sock.say(msg[3], self.stream.now_playing())
			
			elif Text[0] == 'url':
				self.sock.say(msg[3], self.stream.send_url())
				
			elif Text[0] == 'status':
				self.sock.say(msg[3], self.stream.status())
				
			elif Text[0] == 'title':
				self.sock.say(msg[3], self.stream.title())
				
		except Exception, e:
			print("* [Stream] Error:\n* [Stream] {0}".format(str(e)))
			
	def Quote(self, msg):
		'''
		The main quote command. We check for any other data in the msg sent.
		If its a number, we assume they are searching for a specific quote.
		'''
		try:
			if msg[4].split()[1:]:
				Text = msg[4].split()[1:][0]
			else:
				Text = None
			self.sock.say(msg[3], self.IRCq.Number(QuoteNum=Text))
		except:
			pass
	
	def QuoteSearch(self, msg):
		'''Call the Search function of Quotes.py which uses re to find a quote'''	
		if msg[4].split()[1:]:
			Text = " ".join(msg[4].split()[1:])
		else:
			Text = ''
		self.sock.say(msg[3], self.IRCq.Search(msg=Text))
		
	def QuoteCount(self, msg):
		'''Returns the count of total quotes'''
		self.sock.say(msg[3], self.IRCq.Count())
	
	def QuoteAdd(self, msg):
		'''Calls the add function to add a quote'''
		try:
			if msg[4].split()[1:]:
				q = " ".join(msg[4].split()[1:])
			self.sock.say(msg[3], self.IRCq.Add(QuoteString=q))
		except:
			pass
				
	def QuoteDel(self, msg):
		'''Calls the del function to remove a quote'''
		try:
			Text = int(msg[4].split()[1:][0])
		except:
			Text = None
		self.sock.say(msg[3], self.IRCq.Del(QuoteNum=Text))
		
	def QuoteBackup(self, msg):
		'''Calls the backup function to backup the pickled quotes file in plaintext'''
		try:
			Text = msg[4].split()[1:][0]
		except:
			Text = None
		self.sock.say(msg[3], self.IRCq.Backup(BackupFile=Text))
		
	def Rule(self, msg):
		'''Calls Rule function of the IRCRules object'''
		try:
			Num = int(msg[4].split()[1:][0])
		except:
			Num = None
		self.sock.say(msg[3], self.IRCr.Rule(Num=Num))
		
	def RandRule(self, msg):
		'''Calls the Random fucntion of the IRCRules object'''
		self.sock.say(msg[3], self.IRCr.Random())


		# Non-CommandVar Commands:
	def Hug(self, msg):
		check = self.allowed.levelCheck(msg[0])[1]
		if check[1] <= 4:
			self.sock.say(msg[3], "\x01ACTION hugs {0}.\x01".format(msg[0]))
		else:
			self.sock.say(msg[3], "\x01ACTION kicks {0} in the balls for not being a man\x01".format(msg[0]))
	
	def TinyboardLink(self, msg):
		link = "http"+msg[4].split("http")[1].split(" ")[0]		
		self.sock.say(msg[3], self.chon.Main(link))
