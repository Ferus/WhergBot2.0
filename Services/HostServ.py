#!/usr/bin/env python

class HostServ(object):
	'''Hostserv On/Off controls.'''
	def __init__(self, sock=None):
		if sock:
			self.sock = sock

	def On(self):
		print("* [HostServ] Turning vHost on.")
		self.sock.say("HostServ", "On")

	def Off(self):
		print("* [HostServ] Turning vHost off.")
		self.sock.say("HostServ", "Off")

	def Request(self, vHost):
		if vHost:
			print("* [HostServ] Requesting vHost.")
			self.sock.say("HostServ", "Request {0}".format(vHost))
		else:
			return None
