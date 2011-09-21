#!/usr/bin/python2

class Commands():
	def __init__(self, nick='', sock=None, parser=None):
		'''Here we define a dictionary of commands with access levels, and what to do if they are called.
		Each command receives the raw message in a list. Optional socket allows for sending messages.'''
		
		self.nick = nick
		
		if sock:
			self.sock = sock
		
		if parser:
			self.parser = parser
			
		self.cmds = {
			'echo': [self.Echo, 4],
			'raw': [self.Raw, 0],
			'names': [self.Names, 5],
			'join': [self.Join, 3],
			'part': [self.Part, 3],
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
		try:
			#self.sock.say(msg[3], str(self.parser.users))
			print self.parser.users
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
	
	
	
			
			
