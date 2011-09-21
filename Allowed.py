#!/usr/bin/python2


class Users():
	def __init__(self):
		'''Permissions for our bot.'''
		
		self.db = {}
		
	def addOwner(self, nick, host):
		self.db[nick] = [host, 0]
		
	def addAdmin(self, nick, host):
		self.db[nick] = [host, 1]
		
	def addOther(self, nick, host, level):
		'''This is only temporary...'''
		self.db[nick] = [host, int(level)]
		
	def levelCheck(self, nick):
		if nick in self.db.keys():
			return nick, self.db[nick]
		else:
			return None
		
