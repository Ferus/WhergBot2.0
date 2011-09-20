#Global Imports
from blackbox import blackbox_core
import time

#Local Imports
import Parser
import Commands
import Allowed

class Bot():
	def __init__(self, nickname='', realname = '', ident = '', owner = []):
		'''Create our bots name, realname, and ident, and create our IRC object, Commands object, Parser object, and users dict'''
		self.irc = blackbox_core.Core(logging=True)
		self.p = Parser.Parse()
		self.command = Commands.Commands(sock=self.irc)
		self._commands = self.command.cmds.keys()
		
#		self.allow = Allowed.Users()
#		if owner:
#			self.allow.addOwner(owner[0], owner[1])
#		Disabled
		self.allowed = {}
		if owner:
			self.allowed[owner[0]] = [owner[1], owner[2]]
		
		
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

		self.users = {} #Storage for Users of each channel. The Key is channel, users are a list.
		
	def Connect(self, server, port=6667):
		'''Connect to the server'''
		self.irc.connect(server, port)
		print("Connecting to {0} on port {1}".format(server, port))
		time.sleep(.3)
		self.irc.username(self.ident, self.realname)
		print("Sending username: {0} and realname: {1}".format(self.ident, self.realname))
		time.sleep(.3)
		self.irc.nickname(self.nickname)
		print("Sending nickname: {0}".format(self.nickname))
		time.sleep(.3)

	def Join(self, channels):
		self.irc.join(channels)
	
	def SendRaw(self, msg):
		self.irc.send(msg)

	def SendMsg(self, location, msg):
		self.SendRaw("PRIVMSG {0} {1}".format(location, msg))
	
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
				self.nick = self.msg[0]
				self.host = self.msg[1]
				self.action = self.msg[2]
				if self.nickname == self.msg[3]:
					self.location = self.nick
				else:
					self.location = self.msg[3]
				self.text = self.msg[4]
				self.cmd = self.msg[5]
			except:
				try:	
					if 'PART' == self.msg.split()[1]:
						self.msg = self.p.Parted(self.msg)
						self.users[self.msg[3]].remove(self.msg[0])
				
					if 'JOIN' == self.msg.split()[1]:
						self.msg = self.p.Joined(self.msg)
						self.users[self.msg[3]].append(self.msg[0])
					
				except:
					pass

#			if ' 353 '+self.nickname in self.msg: ### ADD TO PARSER
#				try:
#					channel, names = self.msg.split(" = ")[1].split(" \r\n")[0].split(" :")
#					names = names.replace('~','').replace('&','').replace('@','').replace('%','').replace('+','').split(' ')
#					self.users[channel] = names
#				except:
#					pass

			try:
				'''Testing shit now.'''				
				if self.cmd[1:] in self._commands:
					if self.allowed[self.nick][1] <= self.command.cmds[self.cmd[1:]][1] and self.host == self.allowed[self.nick][0]:
						(self.command.cmds[self.cmd[1:]])[0](self.msg)
					

							
				if self.cmd == '[join':
					self.Join(self.text.split()[1])
			except:
				pass

			return self.msg
