#!/usr/bin/env python

try:
	from blackbox import blackbox
except ImportError:
	import sys
	sys.exit("* [Core] WhergBot needs the blackbox IRC macros module to run.")
from time import sleep

import Parser
from Services import NickServ, HostServ, Allowed

class Bot(object):
	def __init__(self, nickname='', realname='', ident='', owner=[], ssl=True, proxy=None, logging=False):
		'''Create our bots name, realname, and ident, and create our IRC object, Commands object, Parser object, and users dict'''
		self.irc = blackbox.IRC(logging=logging, ssl=ssl)
		if proxy:
			try:
				print("* [IRC] Attempting to set proxy to {0} on port {1}".format(proxy[0], proxy[1]))
				import socks
				Types = {"http":socks.PROXY_TYPE_HTTP, "socks4":socks.PROXY_TYPE_SOCKS4, "socks5":socks.PROXY_TYPE_SOCKS5}
				Sock = socks.socksocket()
				Sock.setproxy(Types[proxy[2]], proxy[0], proxy[1])
				self.irc._irc = Sock
				print("* [IRC] Set proxy, if the bot fails to connect, the proxy may be bad.\n* [IRC] This does not set a proxy for any HTTP GET/POST/etc requests.")
			except Exception, e:
				print("* [IRC] Failed to set proxy, using none.")
				print(repr(e))

		self.Nickserv = NickServ.NickServ(sock=self.irc)
		self.Hostserv = HostServ.HostServ(sock=self.irc)

		self.allowed = Allowed.Allowed("Services/AllowedUsers.shelve")

		if owner:
			self.Owner = owner
			self.allowed.Owner = self.Owner
			self.allowed.db[self.Owner[0]] = [self.Owner[1], self.Owner[2]] #Reset the owner. Just in case the config changed.
			print("* [Access] Setting owner to {0}, with hostmask {1}".format(self.Owner[0], self.Owner[1]))

		self.p = Parser.Parse(sock=self.irc, allowed=self.allowed, nick=nickname)

		self.nickname = nickname if nickname else 'WhergBot2'
		self.realname = realname if realname else 'WhergBot [Ferus]'
		self.ident = ident if ident else 'Wherg'


	def Connect(self, server, port=6667):
		'''Connect to the server'''
		self.irc.connect(server, port)
		print("* [IRC] Connecting to {0} on port {1}".format(server, port))
		self.irc.username(self.ident, self.realname)
		print("* [IRC] Sending username: {0} and realname: {1}".format(self.ident, self.realname))
		self.irc.nickname(self.nickname)
		print("* [IRC] Sending nickname: {0}".format(self.nickname))

	def Parse(self, msg):
		try:
			return self.p.Main(msg)
		except blackbox.IRCError, e:
			import sys
			sys.exit("* [IRC] Error: {0}".format(e))
		except Exception, e:
			print("* [Error] {0}, {1}".format(repr(e), e.__class__))
			print("* [Error] {0}".format([msg]))