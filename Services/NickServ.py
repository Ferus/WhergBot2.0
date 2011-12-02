#!/usr/bin/python2
from getpass import getpass

class NickServ(object):
	'''Nickserv controls.'''
	def __init__(self, sock=None):
		self.password = getpass("* [NickServ] Enter bot's NickServ pass. (Blank for no pass): ")
		
		if sock:
			self.sock = sock

	def Identify(self):
		print("* [NickServ] Identifying to NickServ.")
		self.sock.say("NickServ", "Identify {0}".format(self.password))

	def Update():
		print("* [NickServ] Updating.")
		self.sock.say("NickServ", "Update")
