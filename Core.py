#Global Imports
from blackbox import blackbox_core
import time

#Local Imports
import Parser
import Allowed

class Bot():
	def __init__(self, nickname='', realname = '', ident = '', owner = [], ssl = True):
		'''Create our bots name, realname, and ident, and create our IRC object, Commands object, Parser object, and users dict'''
		self.irc = blackbox_core.Core(logging=True, logfile="blackbox.txt", ssl=ssl)
		
		self.allowed = Allowed.Users()
		
		if owner:
			self.owner = owner
			self.allowed.owner = self.owner
			self.allowed.db[self.owner[0]] = [self.owner[1], self.owner[2]] #Reset the owner. Just in case the config changed.
			print("* [Access] Setting owner to {0}, with hostmask {1}".format(self.owner[0], self.owner[1]))
		
		self.p = Parser.Parse(sock=self.irc, allowed=self.allowed, nick=nickname)
				
		if nickname:
			self.nickname = nickname
		else:
			self.nickname = 'WhergBot2'
		if realname:
			self.realname = realname
		else:
			self.realname = 'WhergBot [Ferus]'
		if ident:
			self.ident = ident
		else:
			self.ident = 'Wherg'

		
	def Connect(self, server, port=6697):
		'''Connect to the server, default the port to 6697 because SSL'''
		self.irc.connect(server, port)
		print("* [IRC] Connecting to {0} on port {1}".format(server, port))
		time.sleep(.2)
		self.irc.username(self.ident, self.realname)
		print("* [IRC] Sending username: {0} and realname: {1}".format(self.ident, self.realname))
		time.sleep(.2)
		self.irc.nickname(self.nickname)
		print("* [IRC] Sending nickname: {0}".format(self.nickname))
		time.sleep(.2)
		
	def Parse(self, msg):
		self.msg = msg.strip('\r\n')
		#self.raw = self.msg
		
		if not self.msg:
			self.irc._isConnected = False
			self.irc.close()
			raise blackbox_core.IRCError('Killed from server.')
			quit()
			
		else:
			try:
				self.msg = self.p.Main(self.msg)
				# [ Name, Ident@Host, Action, Loc, Text, Cmd ]
			except:
				pass

