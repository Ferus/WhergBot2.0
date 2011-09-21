#!/usr/bin/python2

class Commands():
	def __init__(self, nick='', sock=None):
		'''Here we define a dictionary of commands with access levels, and what to do if they are called.
		Each command receives the raw message in a list. Optional socket allows for sending messages.'''
		
		self.nick = nick
		
		if sock:
			self.sock = sock
		
		self.cmds = {
			'echo': [self.Echo, 4],
					}
	
	def Echo(self, msg):
		try:
			self.sock.send("PRIVMSG {0} :{1}".format(msg[3], " ".join(msg[4].split(" ")[1:]) ))
		except Exception, e:
			print("[Echo] Error")
			print(e)
			
	
	
