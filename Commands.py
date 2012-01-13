#!/usr/bin/python2

import re
import pluginLoader as pL

class Commands():
	def __init__(self, nick=None, parser=None, allowed=None):
		'''Here we define a dictionary of commands with access levels, and what to do if they are called.
		Each command receives the raw message in a list (msg object).
		Every function defined in each command has to receive a 'msg', 'sock', 'allowed', and 'users' object.
				
		['Ferus', 'anonymous@the.interwebs', 'PRIVMSG', '#hacking', '$quit Some quit message.', '$quit']
		msg[4][6:] == "Some quit message."
		'''
		self.nick = nick

		self.parser = parser
		self.allowed = allowed

		self.cmds = {
			# Command name to be called : Block of code to execute, Access level, Hostcheck
			"^@help": [self.Help, 5, False],
			"^@plugins": [self.Plugins, 5, False],
			"^@quit": [self.Quit, 0, True],
			"^@join": [self.Join, 3, True],
			"^@part": [self.Part, 3, True],
			"^@access": [self.Access, 0, True],
			"^@cmdedit": [self.commandchange, 0, True]
			}

		self.helpstrings = {
			#@help alone will give a basic infostring showing how to use @help
			#@help <ModuleName> will give specific info about a module.
			"Help" : """@help takes one argument, the name of a plugin in which you wish to get help for.
To get a list of loaded plugins, use '@plugins'""",
			"Plugins" : "Notices the user with a list of plugins available. You can also '@help <PluginName>' for specific info",
			"Join" : "Tells {0} to join one or more channel(s). Takes channels separated by a comma with or without the leading hashtag.".format(self.nick),
			"Part" : "Tells {0} to part one or more channel(s). Takes channels separated by a comma with or without the leading hashtag.".format(self.nick),
			"Quit" : "Tells {0} to shutdown.".format(self.nick),
			"Access":"""Allows the owner(s) (Access level 0) to modify access levels per user/hostmask
The default level for ignore is anything above 5, but this can be changed easily.
add:	Used to add/change access of a person. Takes 3 arguments, Nick, Host (or 'none'), and an Access Level.
del:	Used to revoke access from a user. Takes 1 argument, Nick.
show:	Used to print the access for a user to a channel. Takes 1 argument, Nick.""",
			"Cmdedit" : "Used to change access of a plugin. Format is `command [access/host] [level/True/False]`"
			}

		self.loadedplugins = []
					
		#Load 'Plugins'
		plugins = pL.load("Plugins")
		for key in plugins.keys():
			print("* [Plugins] Loading '{0}' plugin from '{1}'".format(key, str(plugins[key])))
			try:
				if hasattr(plugins[key], "hooks"):
					comm = plugins[key].hooks
					for _k in comm.keys():
						self.cmds[_k] = comm[_k]
						print("* [Plugins] Added command '{0}'".format(_k))
					if hasattr(plugins[key], "helpstring"):
						self.helpstrings[key] = plugins[key].helpstring
					else:
						self.helpstrings[key] = "{0} seems to have forgotten to put a helpstring in for this command, please bug him/her about it.".format(self.allowed.Owner[0])
						print("* [Plugins] {0} has no 'helpstring' attribute, You might want to add one.".format(key))
				else:
					print("* [Plugins] {0} has no 'hooks' attribute, passing.".format(key))
			except:
				print("* [Plugins] Failed to load plugin '{0}'".format(key))
		del plugins

	def Help(self, msg, sock, users, _allowed):
		try:
			x = msg[4].split()[1]
		except:
			return None
		if x in self.helpstrings.keys():
			for string in self.helpstrings[x].splitlines():
				sock.notice(msg[0], string)
		else:
			sock.notice(msg[0], "No plugin found with name '{0}'; Loaded plugins with help strings include:".format(x))
			sock.notice(msg[0], ", ".join(self.helpstrings.keys()))

	def Plugins(self, msg, sock, users, _allowed):
		sock.notice(msg[0], ", ".join(self.helpstrings.keys()))
				
	def Join(self, msg, sock, users, _allowed):
		sock.join(msg[4][6:])
			
	def Part(self, msg, sock, users, _allowed):
		if not msg[4][6:]:
			sock.part(msg[3])
			del users.Userlist[msg[3]]
		else:
			sock.part(msg[4][6:])
			del users.Userlist[msg[4][6:]]
	
	def Quit(self, msg, sock, users, _allowed):
		if type(msg) == list:
			msg = msg[4][6:]
			if msg == '':
				msg = "Quitting!"
		elif type(msg) == str:
			msg = msg
		sock.quit(msg)
		print("* [IRC] Quitting with message '{0}'.".format(msg))
		sock.close()
		print("* [IRC] Closing Socket.")
		quit()
	
	def Access(self, msg, sock, users, _allowed):
		Nick = msg[0]
		Host = msg[1]
		Action = msg[2]
		Location = msg[3]
		Text = msg[4]
		try:
			tmp = Text.split()[1:]
			
			if tmp[0] == 'add':
				if tmp[2].lower() == 'none':
					tmp[2] = None
					
				if tmp[1] == self.allowed.Owner[0]:
					sock.say(Location, "You cannot change your access.")
					print("* [Access] Denied changing owners access.")
					return None

				try:
					self.allowed.Add(tmp[1], tmp[2], int(tmp[3]))		
					sock.say(Location, "{0}, {1} added at level {2}".format(tmp[1], tmp[2], tmp[3]))
					print("* [Access] {0}, {1} added at level {2}.".format(tmp[1], tmp[2], tmp[3]))
					self.allowed.Save()
				except:
					sock.say(Location, "Failed to update access for '{0}'".format(tmp[1]))
					print("* [Access] Failed to update access for '{0}'".format(tmp[1]))
						
			elif tmp[0] == 'del':
				if self.allowed.levelCheck(tmp[1]):
					if tmp[1] != self.allowed.Owner[0]:
						del self.allowed.db[tmp[1]]
						sock.say(Location, "Deleted access for {0}".format(tmp[1]))
						print("* [Access] Deleted access for {0}.".format(tmp[1]))
						self.allowed.Save()
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

	def commandchange(self, msg, sock, users, _allowed):
		'''
		A command to edit access values in the cmds dict
		@cmdedit command access/host level/True/False
		
		Be careful not to change an important commands access level
		'''
		tmp = msg[4].split()[1:]
		if len(tmp) != 3:
			sock.say(msg[3], "Format is `{0} command [access/host] [level/True/False]`".format(msg[-1]))
			return None
		try:
			#[command, tochange, value]
			if tmp[0] not in self.cmds.keys():
				sock.say(msg[3], "Could not find that command.")
				return None
				
			if tmp[1] == 'access':
				if tmp[2].isdigit():
					self.cmds[tmp[0]][1] = int(tmp[2])
					sock.say(msg[3], "Changed level access of {0} to {1}.".format(tmp[0], tmp[2]))
				else:
					sock.say(msg[3], "{0} is not a number.".format(tmp[2]))

			elif tmp[1] == 'host':
				_tf = {'true':True, 'false':False}
				if tmp[2].lower() in _tf.keys():
					self.cmds[tmp[0]][2] = _tf[tmp[2].lower()]
					sock.say(msg[3], "Changed hostcheck of {0} to {1}.".format(tmp[0], tmp[2]))
				else:
					sock.say(msg[3], "{0} is not True or False.".format(tmp[2]))
			else:
				return None
		except Exception, e:
			print("* [Access] Error: {0}".format(repr(e)))
					
