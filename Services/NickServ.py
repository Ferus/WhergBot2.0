#!/usr/bin/env python
from getpass import getpass

class NickServ(object):
	'''Nickserv controls.'''
	def __init__(self, sock=None):
		try:
			self.password = getpass("* [NickServ] Enter bot's NickServ pass. (Blank for no pass): ")
		except EOFError:
			print("")
			self.password = ''

		if sock:
			self.sock = sock

	def Identify(self):
		print("* [NickServ] Identifying to NickServ.")
		self.sock.say("NickServ", "Identify {0}".format(self.password))

	def Update(self):
		print("* [NickServ] Updating.")
		self.sock.say("NickServ", "Update")
