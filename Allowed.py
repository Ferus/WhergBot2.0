#!/usr/bin/python2


class Users():
	def __init__(self):
		'''Permissions for our bot.'''
		
		self.db = {}
		
	def addOwner(self, nick, host):
		self.db[nick] = [host, 0]
		
	def addAdmin(self, nick, host):
		self.db[nick] = [host, 1]
		
	def levelCheck(self, nick):
		if nick in self.db.keys():
			return self.db[nick]
		else:
			return None
		
