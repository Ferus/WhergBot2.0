#!/usr/bin/python2

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
			
		self.cmds = {
			# Command name to be called : Block of code to execute, Access level, Hostcheck
			'echo': [self.Echo, 4, False],
			'raw': [self.Raw, 0, True],
			'names': [self.Names, 0, False],
			'join': [self.Join, 3, True],
			'part': [self.Part, 3, True],
			'quit': [self.Quit, 0, True],
					}
	
	def Echo(self, msg):
		try:
			self.sock.say(msg[3], msg[4][6:])
		except Exception, e:
			print("* [Echo] Error")
			print(e)
			
	def Raw(self, msg):
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
		msg = msg[4][6:]
		if msg == '':
			msg = "Quitting!"
			
		self.sock.quit(msg)
		print("* [IRC] Quitting with message '{0}'.".format(msg))
		self.allowed.db.close()
		print("* [Allowed] Closing database.")
		self.sock.close()
		print("* [IRC] Closing Socket.")
		quit()
			
			

