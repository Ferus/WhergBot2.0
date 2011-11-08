#!/usr/bin/python2
import shelve

class Users():
	def __init__(self):
		'''Permissions for our bot.
		Dictionary holds user names as keys, 
		and a list containing the host and access level
		'''
		
		_db = shelve.open("Allowed_Users")
		self.db = self.dump(_db)
		_db.close()
			
		self.keys = self.db.keys()
		self.owner = None
		
	def addOwner(self, nick, host):
		self.db[nick] = [host, 0]
		
	def addAdmin(self, nick, host):
		self.db[nick] = [host, 1]
		
	def addOther(self, nick, host, level):
		'''This is only temporary until I think of names for the others.'''
		self.db[nick] = [host, int(level)]
		
	def levelCheck(self, nick):
		if nick in self.db.keys():
			return nick, self.db[nick]
		else:
			return None
			
	def dump(self, db):
		x = {}
		for key in db.keys():
			x[key] = db[key]
		return x
		
	def save(self):
		try:
			_db = shelve.open("Allowed_Users")
			for key in self.db.keys():
				_db[key] = self.db[key]
			_db.close()
			return True
		except:
			return False
