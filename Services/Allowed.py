#!/usr/bin/python2
import shelve

class Allowed():
	def __init__(self, db=None):
		'''Permissions for our bot.
		Dictionary holds user names as keys, 
		and a list containing the host and access level
		'''
		if db:
			self._dbFile = db
		else:
			self._dbFile = "Services/AllowedUsers.shelve"
			
		_db = shelve.open(self._dbFile)
		self.db = self.Load(_db)
		_db.close()
			
		self.keys = self.db.keys()
		self.Owner = None
		
	def Add(self, nick, host, level):
		self.db[nick] = [host, int(level)]
		self.Save()
		
	def levelCheck(self, nick):
		if nick in self.db.keys():
			return nick, self.db[nick]
		else:
			return None
			
	def Load(self, db):
		x = {}
		for key in db.keys():
			x[key] = db[key]
		return x
		
	def Save(self):
		try:
			_db = shelve.open(self._dbFile)
			for key in self.db.keys():
				_db[key] = self.db[key]
			_db.close()
			print("* [Access] Saving database.")
			return True
		except:
			return False
