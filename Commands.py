#!/usr/bin/python2

from Plugins import Meme, SloganMaker, UrbanDictionary

class Commands():
	def __init__(self, nick=None, sock=None, parser=None, allowed=None):
		'''Here we define a dictionary of commands with access levels, and what to do if they are called.
		Each command receives the raw message in a list. Optional socket allows for raw IRC commands.
		
		Every function defined in here has to receive a 'msg' variable, which is a list returned from the parser. IE:
		['Ferus', 'anonymous@the.interwebs', 'PRIVMSG', '#hacking', '$quit Some quit message.', '$quit']
		msg[4][6:] == "Some quit message."
		'''
		
		self.nick = nick
		
		self.sock = sock
		self.parser = parser
		self.allowed = allowed
		
		### PLUGIN OBJECTS
		self.M = Meme.meme()
			
		self.cmds = {
			# Command name to be called : Block of code to execute, Access level, Hostcheck
			'echo': [self.Echo, 4, False],
			'raw': [self.Raw, 0, True],
			'names': [self.Names, 0, False],
			'join': [self.Join, 3, True],
			'part': [self.Part, 3, True],
			'quit': [self.Quit, 0, True],
			'access': [self.Access, 0, True],
			'meme': [self.Meme, 5, False],
			'slogan': [self.Slogan, 5, False],
			'ud': [self.UD, 5, False],
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
		self.allowed.db.close()
		print("* [Allowed] Closing database.")
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


