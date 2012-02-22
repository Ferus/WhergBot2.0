#!/usr/bin/env python

class Users(object):
	def __init__(self):
		'''
		Stores a dict of Channel keys, with User lists.
		IE: Userlist['#Example'] = ['User1', 'User2', 'etc']
		'''
		self.Userlist = {}

	def GetUserList(self, channel):
		'''
		Return a list of users for a given channel.
		'''
		try:
			return self.Userlist[channel]
		except:
			return None
