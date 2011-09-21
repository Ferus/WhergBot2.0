#!/usr/bin/python2
#import Allowed (better name?)
#I need an allowed.py that holds user levels in dictionaries. {'Person':['Host','Level',etc],}

class Parse():
	def __init__(self, sock=None, nick=''):
		if sock:
			self.sock = sock
		
		if nick:
			self.nickname = nick
		
		self.users = {} #Storage for Users of each channel. The Key is channel, users are a list.
		
	def Main(self, msg):
		'''Main Parser, Here we take raw data, split at \r\n, and add it to a buffer.'''
		tmp = msg.splitlines()

		if len(tmp) >1: #Somehow this handles the bunched up lists when connecting. Weird.
			for msg in tmp:
				msg = msg.split()
				print(msg)
				
				try:				
					if msg[1] == '353' and msg[2] == self.nickname:
						nameslist = []
						for x in msg[5:]:
							x = x.replace(":","").replace("~","").replace("&","").replace("@","").replace("%","").replace("+","")
							nameslist.append(x)
						self.users[msg[4]] = nameslist					
				except:
					pass
					
		else:
			for msg in tmp:
				tmp = msg
				msg = msg.split()
				print(msg)

				try:
					# Parts, Joins, Kicks, All IRC actions
					# CTCP: '\x01TIME\x01' ['Ferus', 'anonymous@the.interwebs', 'PRIVMSG', 'WhergBot2', '\x01TIME\x01', '\x01TIME\x01']

					if msg[1] == 'KICK' and msg[3] == self.nickname:
						self.sock.send("JOIN {0}".format(msg[2]))
				
					if msg[1] == 'PRIVMSG':
						l = self.Privmsg(tmp)
						return l
				
					if msg[1] == 'NOTICE':
						l = self.Notice(tmp)
						return l
			

					if msg[1] == 'JOIN':
						self.users[msg[2].strip(":")].append(msg[0].split("!")[0].strip(":"))
					if msg[1] == 'PART':
						self.users[msg[2]].remove(msg[0].split("!")[0].strip(":"))
					if msg[1] == 'QUIT':
						person = msg[0].split("!")[0]
						for chan in self.users.keys():
							if person in self.users[chan]:
								self.users[chan].remove(person)
					
					else:
						return msg
	
				except:
					#Return the raw msg, if all else fails.
					#return ['','','','','','']
				
					#Return the raw message instead, (but only because I havent finished the parser >_>)
					return msg

	def Privmsg(self, msg):
		return [
			self.Nick(msg),
			self.Host(msg),
			self.Action(msg),
			self.Loc(msg),
			self.Text(msg),
			self.Cmd(msg)
			]
			
	def Notice(self, msg):
		return [
			self.Nick(msg),
			self.Host(msg),
			self.Action(msg),
			self.Loc(msg),
			self.Text(msg)
			]	
	
	
	def Nick(self, msg):
		try:
			n = msg.split("!")[0].strip(":")
			return n
		except:
			return ''
			
	def Host(self, msg):
		try:
			h = msg.split("!")[1].split(" ")[0]
			return h
		except:
			return ''
		
	def Text(self, msg):
		try:
			t = msg.split(" :")[1]
			return t
		except:
			return ''
		
	def Cmd(self, msg):
		try:
			c = msg.split(" :")[1].split()[0]	
			return c
		except:
			return ''
	
	def Loc(self, msg):
		try:
			l = msg.split()[2]
			return l
		except:
			return ''
	
	def Action(self, msg):
		try:
			a = msg.split()[1]
			return a
		except:
			return ''
			
	def Pinged(self, msg):
		try:
			p = msg.split()[1].strip(":")
			return p
		except:
			return ''
			
	def Joined(self, msg):
		msg = msg.split()
		return [self.Nick(msg[0]), self.Host(msg[0]), msg[1], msg[2].strip(":")]
	
	def Parted(self, msg):
		msg = msg.split()
		return [self.Nick(msg[0]), self.Host(msg[0]), msg[1], msg[2]]

			
