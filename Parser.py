#!/usr/bin/python2
#import Allowed (better name?)
#I need an allowed.py that holds user levels in dictionaries. {'Person':['Host','Level',etc],}

class Parse():
	def __init__(self):
		pass
		
	def Main(self, msg):
		'''Main Parser, Here we take raw data, split at \r\n, and add it to a buffer.'''
		tmp = msg.splitlines()

		for msg in tmp:
			
			tmp = msg
			msg = msg.split()
	
			try:
				# Parts, Joins, Kicks, All IRC actions
				# CTCP: '\x01TIME\x01' ['Ferus', 'anonymous@the.interwebs', 'PRIVMSG', 'WhergBot2', '\x01TIME\x01', '\x01TIME\x01']
			
				if msg[1] == 'PRIVMSG':
					l = self.Privmsg(tmp)
					return l
				
				if msg[1] == 'NOTICE':
					l = self.Notice(tmp)
					return l
				
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

			
