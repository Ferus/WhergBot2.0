#!/usr/bin/env python

import re
import pluginLoader as pL
from Plugins import CommandLock

class Commands():
	def __init__(self, nick=None, parser=None, allowed=None):
		'''Here we define a dictionary of commands with access levels, and what to do if they are called.
		Every function defined for command has to receive a 'msg', 'sock', 'allowed', and 'users' object.

		['Ferus', 'anonymous@the.interwebs', 'PRIVMSG', '#hacking', '$quit Some quit message.', '$quit']
		msg[4][6:] == "Some quit message."

		sock.say("#channel", "Hi!")
		'''
		self.nick = nick

		self.parser = parser
		self.allowed = allowed

		self.Locker = CommandLock.Locker(-1)

		self.cmds = {"^@help": [self.Help, 5, False]
			,"^@plugins": [self.Plugins, 5, False]
			,"^@quit": [self.Quit, 0, True]
			,"^@join": [self.Join, 3, True]
			,"^@part": [self.Part, 3, True]
			,"^@access": [self.Access, 0, True]
			,"^@lock": [self.Lock, 0, True]
			,"^@unlock": [self.Unlock, 0, True]
			}

		self.helpstrings = {
			#@help alone will give a basic infostring showing how to use @help
			#@help <ModuleName> will give specific info about a module.
			"help" : """@help takes one argument, the name of a plugin in which you wish to get help for.
					 To get a list of loaded plugins, use '@plugins'
					 """
			,"plugins" : "Notices the user with a list of plugins available. You can also '@help <PluginName>' for specific info"
			,"join" : "Tells {0} to join one or more channel(s). Takes channels separated by a comma with or without the leading hashtag.".format(self.nick)
			,"part" : "Tells {0} to part one or more channel(s). Takes channels separated by a comma with or without the leading hashtag.".format(self.nick)
			,"quit" : "Tells {0} to shutdown.".format(self.nick)
			,"access": """Allows the owner(s) (Access level 0) to modify access levels per user/hostmask
				The default level for ignore is anything above 5, but this can be changed.
				add:	Used to add/change access of a person. Takes 3 arguments, Nick, Host (or 'none'), and an Access Level.
				del:	Used to revoke access from a user. Takes 1 argument, Nick.
				show:	Used to print the access for a user to a channel. Takes 1 argument, Nick.
				"""
			,"lock": "Locks all commands down to Owner access only."
			,"unlock": "Unlocks all commands."
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
						self.helpstrings[key.lower()] = plugins[key].helpstring
					else:
						self.helpstrings[key.lower()] = "{0} seems to have forgotten to put a helpstring in for this command, please bug him/her about it.".format(self.allowed.Owner[0])
						print("* [Plugins] {0} has no 'helpstring' attribute, You might want to add one.".format(key))
				else:
					print("* [Plugins] {0} has no 'hooks' attribute, passing.".format(key))
			except:
				print("* [Plugins] Failed to load plugin '{0}'".format(key))
		del plugins

	def Help(self, msg, sock, users, _allowed):
		try:
			x = msg[4].split()[1].lower()
		except:
			x = ''
		if x in self.helpstrings.keys():
			for string in self.helpstrings[x].splitlines():
				sock.notice(msg[0], string.strip('\t'))
		elif x == '':
			sock.notice(msg[0], self.helpstrings['help'])
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
			for x in msg[4][6:].split():
				del users.Userlist[x]


	def Quit(self, msg, sock, users, _allowed):
		if type(msg) == list:
			msg = msg[4][6:]
			if msg == '':
				msg = "Quitting!"
		elif type(msg) == unicode:
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
			sock.notice(Nick, "Format for 'access' is: `access add/del Nick Ident@host Level`")
			print("* [Access] Error:\n* [Access] {0}".format(str(e)))

	def Lock(self, msg, sock, users, _allowed):
		if not self.Locker.Locked:
			if self.Locker.Lock():
				sock.say(msg[3], "Locking successful.")
		else:
			sock.notice(msg[0], "I'm already locked you derp.")

	def Unlock(self, msg, sock, users, _allowed):
		if self.Locker.Locked:
			if not self.Locker.Unlock():
				sock.say(msg[3], "Unlocking successful.")
		else:
			sock.notice(msg[0], "I'm already unlocked you derp.")