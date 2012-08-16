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

def formattime():
	return strftime(Config.Global['timeformat'])

class Connection(object):
	"""A connection instance for a server
	"""
	def __init__(self, name, conf, Connections, Processes):
		self.__time__ = time()
		self.__name__ = name
		self.Connections = Connections
		self.Processes = Processes
		self.Config = conf
		self.IRC = blackbox.IRC(ssl=self.Config.get('ssl', False))
		self.Parser = Parser.Parser(self)
		self.shuttingDown = False

	def makeConnection(self):
		try:
			self.IRC.connect(self.Config.get('host'), self.Config.get('port'))
			print("{0} Initializing connection for server {1}.".format(formattime(), self.__name__))
			self.IRC.nickname(self.Config.get('nick'))
			print("{0} Sending Nickname to server {1}.".format(formattime(), self.__name__))
			self.IRC.username(self.Config.get('ident'), self.Config.get('realname'))
			print("{0} Sending Ident and Realname to server {1}.".format(formattime(), self.__name__))
		except Exception as e:
			print("{0} Exception when making connection to server {1}:".format(formattime(), self.__name__))
			print("{0} {1}".format(formattime(), repr(e.args)))
			sleep(15)
			self.makeConnection()

	def quitConnection(self):
		self.shuttingDown = True
		for Plugin, Values in list(self.Parser.loadedPlugins.items()):
			Values[5]()
			print("* Running Unload on plugin '{0}'".format(Plugin))
		self.IRC.quit(self.Config.get('quitmessage', 'KeyboardInterrupt raised; Quitting!'))
		print("{0} {1}: Quitting Server!".format(formattime(), self.__name__))
		return True

	def parseData(self, data=None):
		if data:
			self.Parser.Parse(data)
		else:
			while not self.shuttingDown:
				try:
					self.Parser.Parse(self.IRC.recv())
				except blackbox.IRCError as e:
					print("{0} IRCError on connection '{1}': {2}".format(formattime(), self.__name__, repr(e)))
					self.Connections.remove(self)
					print("{0} Connection '{1}' removed.".format(formattime(), self.__name__))
					if not self.shuttingDown:
						print("{0} Attempting to reconnect.".format(formattime()))
						run(self.__name__, self.Config)
					return None
				except Exception as e:
					print("{0} Exception caught on connection '{1}': {2}".format(formattime(), self.__name__, repr(e)))
			return None

def run(Name, Server): #change to allow passing of one dictionary and name rather than the name of the dictionary
	if not Server['enabled']:
		print("{0} Skipping disabled server {1}".format(formattime(), Name))
		return
	print("{0} Loading Config for server '{1}'".format(formattime(), Name))

	C = Connection(name=Name, conf=Server, Connections=Connections, Processes=Processes)
	C.makeConnection()
	Connections.append(C)
	try:
		while True:
			tempData = C.IRC.recv()
			C.parseData(tempData)
			if '001' in tempData:
				break
		while C.Parser._onConnect:
			try:
				C.Parser._onConnect.pop(0)()
			except Exception as e:
				print("{0} Error with function in _onConnect: {1}".format(formattime(), repr(e)))
		sleep(1)
		C.IRC.join(Server.get('channels'))
	except blackbox.IRCError as e:
		print("{0} Removing Conn {1}: {2}".format(formattime(), C.__name__, repr(e)))
		Connections.remove(C)
	except Exception as e:
		print(repr(e))

	p = Thread(target=C.parseData)
	p.name = C.__name__
	p.daemon = True
	p.start()
	Processes.append(p)

if __name__ == '__main__':
	Connections = []
	Processes = []
	for Name, Server in list(Config.Servers.items()):
		run(Name, Server)

	try:
		while len(Processes) > 0:
			Processes = [p for p in Processes if p.is_alive()]
			sleep(5)
	except KeyboardInterrupt:
		print('\n')
		for Conn in Connections:
			Conn.quitConnection()
		while len(Processes) > 0:
			Processes = [p for p in Processes if p.is_alive()]
			sleep(1)
	finally:
		sys.exit()
