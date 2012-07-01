#!/usr/bin/env python
import sys
from threading import Thread
from time import sleep, strftime, time
try:
	from blackbox import blackbox
except ImportError:
	sys.exit("The blackbox IRC Macros module is needed to run.")

import Config
import Parser

class Connection(object):
	"""A connection instance for a server
	"""
	def __init__(self, name, conf, Connections, Processes):
		self.__time__ = time()
		self.__name__ = name
		self.Connections = Connections
		self.Processes = Processes
		self.Config = conf
		self.IRC = blackbox.IRC(logging=self.Config.get('logging', False)
			,logfile=self.Config.get('logfile', "{0}.log".format(self.__name__))
			,ssl=self.Config.get('ssl', False))
		self.Parser = Parser.Parser(self)
		self.shuttingDown = False

	def makeConnection(self):
		try:
			self.IRC.connect(self.Config.get('host'), self.Config.get('port'))
			print("{0} Initializing connection for server {1}.".format(strftime(Config.Global['timeformat']), self.__name__))
			self.IRC.nickname(self.Config.get('nick'))
			print("{0} Sending Nickname to server {1}.".format(strftime(Config.Global['timeformat']), self.__name__))
			self.IRC.username(self.Config.get('ident'), self.Config.get('realname'))
			print("{0} Sending Ident and Realname to server {1}.".format(strftime(Config.Global['timeformat']), self.__name__))
		except Exception, e:
			print("{0} Exception when making connection to server {1}:".format(strftime(Config.Global['timeformat']), self.__name__))
			print("{0} {1}".format(strftime(Config.Global['timeformat']), repr(e)))
			sleep(1)
			self.makeConnection()
	
	def quitConnection(self):
		self.shuttingDown = True
		for Plugin, Values in self.Parser.loadedPlugins.items():
			Values[5]()
			print("* Running Unload on plugin '{0}'".format(Plugin))
		self.IRC.quit(self.Config.get('quitmessage', 'KeyboardInterrupt raised; Quitting!'))
		print("{0} {1}: Quitting Server!".format(strftime(Config.Global['timeformat']), self.__name__))
		return True
	
	def parseData(self, data=None):
		if data:
			self.Parser.Parse(data)
		else:
			while not self.shuttingDown:
				try:
					self.Parser.Parse(self.IRC.recv().encode('utf8'))
				except blackbox.IRCError, e:
					print("{0} IRCError on connection '{1}': {2}".format(strftime(Config.Global['timeformat']), self.__name__, repr(e)))
					self.Connections.remove(self)
					print("{0} Connection '{1}' removed.".format(strftime(Config.Global['timeformat']), self.__name__))
					if not self.shuttingDown:
						print("{0} Attempting to reconnect.".format(strftime(Config.Global['timeformat'])))
						run([self.__name__])
					return None
				except Exception, e:
					print("{0} Exception caught on connection '{1}': {2}".format(strftime(Config.Global['timeformat']), self.__name__, repr(e)))
			return None

def run(servers):
	Conns = []
	Processes = []
	for Server in servers:
		if not Config.Servers[Server]['enabled']:
			print("{0} Skipping disabled server {1}".format(strftime(Config.Global['timeformat']), Server))
			continue
		print("{0} Loading Config for server '{1}'".format(strftime(Config.Global['timeformat']), Server))

		C = Connection(name=Server, conf=Config.Servers[Server], Connections=Conns, Processes=Processes)
		Conns.append(C)
	[x.makeConnection() for x in Conns]

	for Conn in Conns:
		try:
			while True:
				tempData = Conn.IRC.recv()
				Conn.parseData(tempData)
				if '001' in tempData:
					break
			while Conn.Parser._onConnect:
				try:
					Conn.Parser._onConnect.pop(0)()
				except Exception, e:
					print("{0} Error with function in _onConnect: {1}".format(strftime(Config.Global['timeformat']), repr(e)))
			sleep(1)
			Conn.IRC.join(Conn.Config.get('channels'))
		except blackbox.IRCError, e:
			print("{0} Removing Conn {1}: {2}".format(strftime(Config.Global['timeformat']), Conn.__name__, repr(e)))
			Conns.remove(Conn)
		except Exception, e:
			print(repr(e))
		
		p = Thread(target=Conn.parseData)
		p.name = Conn.__name__
		p.daemon = True
		p.start()
		Processes.append(p)
	try:
		while len(Processes) > 0:
			Processes = [p for p in Processes if p.is_alive()]
			sleep(5)
	except KeyboardInterrupt:
		print('\n')
		for Conn in Conns:
			Conn.quitConnection()
		while len(Processes) > 0:
			Processes = [p for p in Processes if p.is_alive()]
			sleep(1)
	finally:
		sys.exit()

if __name__ == '__main__':
	run(Config.Servers.keys())
