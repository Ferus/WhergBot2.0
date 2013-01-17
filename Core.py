#!/usr/bin/python3.2
import sys
import threading
import time
import logging
import socket
try:
	import blackbox
except ImportError:
	sys.exit("The blackbox IRC Macros module is needed to run.")

import Config
import Parser

logging.basicConfig(filename="Wherg.log", filemode='w', level=logging.INFO
		,format="%(levelname)s - %(asctime)s - %(name)s - %(filename)s - %(funcName)s() - Line: %(lineno)d - %(message)s")
logger = logging.getLogger("Core")

class Connection(object):
	"""A connection instance for a server
	"""
	def __init__(self, name, conf):
		self.__time__ = time.time()
		self.__name__ = name
		self.Connections = Connections
		self.Processes = Processes
		self.Config = conf
		self.IRC = blackbox.Oper(ssl=self.Config.get('ssl', False))
		self.Parser = Parser.Parser(self)
		self.shuttingDown = False

	def makeConnection(self):
		try:
			self.IRC.connect(self.Config.get('host'), self.Config.get('port'))
			logger.info("Initializing connection for server {0}.".format(self.__name__))
			self.IRC.nickname(self.Config.get('nick'))
			logger.info("Sending Nickname to server {0}.".format(self.__name__))
			self.IRC.username(self.Config.get('ident'), self.Config.get('realname'))
			logger.info("Sending Ident and Realname to server {0}.".format(self.__name__))
		except Exception as e:
			logger.exception("Exception when making connection to server {0}:".format(self.__name__))
			time.sleep(15)
			self.makeConnection()

	def quitConnection(self):
		self.shuttingDown = True
		for Plugin, Instance in list(self.Parser.loadedPlugins.items()):
			Instance.Unload()
			logger.info("* Running Unload on plugin '{0}'".format(Plugin))
		self.IRC.quit(self.Config.get('quitmessage', 'KeyboardInterrupt raised; Quitting!'))
		logger.info("{0}: Quitting Server!".format(self.__name__))
		return True

	def parseData(self, data=None):
		if data:
			self.Parser.Parse(data)
		else:
			while not self.shuttingDown:
				try:
					self.Parser.Parse(self.IRC.recv())
				except blackbox.IRCError as e:
					logger.exception("IRCError on connection '{0}': {1}".format(self.__name__, repr(e)))
					self.Connections.remove(self)
					logger.info("Connection '{0}' removed.".format(self.__name__))
					if not self.shuttingDown:
						logger.info("Attempting to reconnect to {0}.".format(self.__name__))
						run(self.__name__, self.Config)
					return None
				except Exception as e:
					logger.exception("Exception caught on connection '{0}': {1}".format(self.__name__, repr(e)))
			return None

def run(name, serv): #change to allow passing of one dictionary and name rather than the name of the dictionary
	if not serv['enabled']:
		logging.info("Skipping disabled server '{0}'".format(name))
		return
	logging.info("Loading Config for server '{0}'".format(name))

	C = Connection(name=name, conf=serv)
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
				logger.exception("Error with function in Parser._onConnect")
		C.IRC.join(serv.get('channels'))
	except blackbox.IRCError as e:
		logger.exception("Removing Conn {0}".format(C.__name__))
		Connections.remove(C)
	except socket.error as e:
		Connections.remove(C)
		if e.errno == 104:
			# Weird bug.
			logger.exception("Socket Error 104")
		run(name, serv)
		logger.info("Attempting to reconnect")
	except Exception as e:
		logger.exception("Error in main function run()")

	p = threading.Thread(target=C.parseData)
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
			time.sleep(5)
	except KeyboardInterrupt:
		print('\n')
		for Conn in Connections:
			Conn.quitConnection()
		while len(Processes) > 0:
			Processes = [p for p in Processes if p.is_alive()]
			time.sleep(1)
	finally:
		sys.exit()
