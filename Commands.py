#!/usr/bin/python2

import re
import pluginLoader as pL

class Commands():
	def __init__(self, nick=None, parser=None, allowed=None):
		'''Here we define a dictionary of commands with access levels, and what to do if they are called.
		Each command receives the raw message in a list. Optional socket allows for raw IRC commands.
		
		Every function defined in here has to receive a 'msg' variable, which is a list returned from 
		the parser and the socket object.
		
		['Ferus', 'anonymous@the.interwebs', 'PRIVMSG', '#hacking', '$quit Some quit message.', '$quit']
		msg[4][6:] == "Some quit message."
		'''
		self.nick = nick

		self.parser = parser
		self.allowed = allowed

		self.cmds = {
			# Command name to be called : Block of code to execute, Access level, Hostcheck
			"^@quit": [self.Quit, 0, True],
			"^@join": [self.Join, 3, True],
			"^@part": [self.Part, 3, True],
			"^@access": [self.Access, 0, True],
			}
					
		#Load 'Plugins'
		plugins = pL.load("Plugins")
		loadedplugins = []
		for key in plugins.keys():
			print("* [Plugins] Loaded '{0}' plugin from '{1}'".format(key, str(plugins[key])))
			try:
				if hasattr(plugins[key], "hooks"):
					loadedplugins.append(key)
					comm = plugins[key].hooks
					for _k in comm.keys():
						self.cmds[_k] = comm[_k]
						print("* [Plugins] Added command '{0}'".format(_k))
			except:
				print("* [Plugins] Failed to load plugin '{0}'".format(key))
		del plugins
				
	def Join(self, msg, sock):
		try:
			sock.join(msg[4][6:])
		except Exception, e:
			print("* [Join] Error")
			print(e)
			
	def Part(self, msg, sock):
		try:
			if not msg[4][6:]:
				sock.part(msg[3])
				del self.parser.users[msg[3]]
			else:
				sock.part(msg[4][6:])
				del self.parser.users[msg[4][6:]]
		except Exception, e:
			print("* [Part] Error")
			print(e)
	
	def Quit(self, msg, sock):
		if type(msg) == list:
			msg = msg[4][6:]
			if msg == '':
				msg = "Quitting!"
		elif type(msg) == str:
			msg = msg
		sock.quit(msg)
		print("* [IRC] Quitting with message '{0}'.".format(msg))
		self.allowed.save()
		print("* [Allowed] Saving database.")
		sock.close()
		print("* [IRC] Closing Socket.")
		quit()
	
	def Access(self, msg, sock):
		Nick = msg[0]
		Host = msg[1]
		Action = msg[2]
		Location = msg[3]
		Text = msg[4]
	
		if self.allowed.db[Nick][1] == 0:
			try:
				levels = {0: self.allowed.addOwner, 1: self.allowed.addAdmin}
				tmp = Text.split()[1:]

				if tmp[0] == 'add':
					if tmp[2] == 'None':
						tmp[2] = None
					
					if tmp[1] == self.allowed.owner[0]:
						sock.say(Location, "You cannot change your access.")
						print("* [Access] Denied changing owners access.")
						return None
						
					if int(tmp[3]) in levels.keys():
						levels[int(tmp[3])](tmp[1], tmp[2])								
					else:
						self.allowed.addOther(tmp[1], tmp[2], int(tmp[3]))
						
					sock.say(Location, "{0}, {1} added at level {2}".format(tmp[1], tmp[2], tmp[3]))
					print("* [Access] {0}, {1} added at level {2}.".format(tmp[1], tmp[2], tmp[3]))
						
				elif tmp[0] == 'del':
					if self.allowed.levelCheck(tmp[1]):
						if tmp[1] != self.allowed.owner[0]:
							del self.allowed.db[tmp[1]]
							sock.say(Location, "Deleted access for {0}".format(tmp[1]))
							print("* [Access] Deleted access for {0}.".format(tmp[1]))
						else:
							sock.say(Location, "Access for {0} cannot be deleted.".format(tmp[1]))
					else:
						sock.say(Location, "No access level found for {0}".format(tmp[1]))
				
				elif tmp[0] == 'show':
					try:								
						sock.say(Location, str(self.allowed.db[tmp[1]]))
					except Exception, e:
						print(e)
						
				
			except Exception, e:
				sock.send("NOTICE {0} :{1}".format(Nick, "Format for 'access' is: `access add/del Nick Ident@host Level`"))
				print("* [Access] Error:\n* [Access] {0}".format(str(e)))

	#A command to edit values in the cmds dict
