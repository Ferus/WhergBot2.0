#!/usr/bin/env python
import os
import glob
import re
import logging
import importlib, imp
import threading

from blackbox.blackbox import IRCError
import Config

logger = logging.getLogger("Parser")

class Parser(object):
	def __init__(self, Connection):
		self.Connection = Connection
		self.IRC = self.Connection.IRC
		self._onConnect = []

		self.Commands = {
				# "PRIVMSG" [self.PRIVMSG, {Plugin: {Regex: Callback}, Plugin2: {Regex: Callback} } ]
			# NON-NUMERICAL responses
			"PRIVMSG": [
				self.PRIVMSG, {
					"Core":
						{'^@quit( .*?)?$': self.Shutdown
						,'^@reload \w+$': self.reLoadPlugins
						,'^@unload \w+$': self.unLoadPlugins
						}
					}
				]

			,"NOTICE": [self.NOTICE, {"Core": {}}]
			,"JOIN": [self.JOIN, {"Core": {}}]
			,"PART": [self.PART, {"Core": {}}]
			,"QUIT": [self.QUIT, {"Core": {}}]
			,"KILL": [self.KILL, {"Core": {}}]
			,"MODE": [self.MODE, {"Core": {}}]
			,"NICK": [self.NICK, {"Core": {}}]
			,"KICK": [self.KICK, {"Core": {}}]
			,"WALLOPS": [self.WALLOPS, {"Core": {}}]

			# COMMAND responses
			,'200': [self.RPL_TRACELINK, {"Core": {}}]
			,'201': [self.RPL_TRACECONNECTING, {"Core": {}}]
			,'202': [self.RPL_TRACEHANDSHAKE, {"Core": {}}]
			,'203': [self.RPL_TRACEUNKNOWN, {"Core": {}}]
			,'204': [self.RPL_TRACEOPERATOR, {"Core": {}}]
			,'205': [self.RPL_TRACEUSER, {"Core": {}}]
			,'206': [self.RPL_TRACESERVER, {"Core": {}}]
			,'208': [self.RPL_TRACENEWTYPE, {"Core": {}}]
			,'211': [self.RPL_STATSLINKINFO, {"Core": {}}]
			,'212': [self.RPL_STATSCOMMANDS, {"Core": {}}]
			,'213': [self.RPL_STATSCLINE, {"Core": {}}]
			,'214': [self.RPL_STATSNLINE, {"Core": {}}]
			,'215': [self.RPL_STATSILINE, {"Core": {}}]
			,'216': [self.RPL_STATSKLINE, {"Core": {}}]
			,'218': [self.RPL_STATSYLINE, {"Core": {}}]
			,'219': [self.RPL_ENDOFSTATS, {"Core": {}}]
			,'221': [self.RPL_UMODEIS, {"Core": {}}]
			,'241': [self.RPL_STATSLLINE, {"Core": {}}]
			,'242': [self.RPL_STATSUPTIME, {"Core": {}}]
			,'243': [self.RPL_STATSOLINE, {"Core": {}}]
			,'244': [self.RPL_STATSHLINE, {"Core": {}}]
			,'251': [self.RPL_LUSERCLIENT, {"Core": {}}]
			,'252': [self.RPL_LUSEROP, {"Core": {}}]
			,'253': [self.RPL_LUSERUNKNOWN, {"Core": {}}]
			,'254': [self.RPL_LUSERCHANNELS, {"Core": {}}]
			,'255': [self.RPL_LUSERME, {"Core": {}}]
			,'256': [self.RPL_ADMINME, {"Core": {}}]
			,'257': [self.RPL_ADMINLOC1, {"Core": {}}]
			,'258': [self.RPL_ADMINLOC2, {"Core": {}}]
			,'259': [self.RPL_ADMINEMAIL, {"Core": {}}]
			,'261': [self.RPL_TRACELOG, {"Core": {}}]
			,'300': [self.RPL_NONE, {"Core": {}}]
			,'301': [self.RPL_AWAY, {"Core": {}}]
			,'302': [self.RPL_USERHOST, {"Core": {}}]
			,'303': [self.RPL_ISON, {"Core": {}}]
			,'305': [self.RPL_UNAWAY, {"Core": {}}]
			,'306': [self.RPL_NOWAWAY, {"Core": {}}]
			,'311': [self.RPL_WHOISUSER, {"Core": {}}]
			,'312': [self.RPL_WHOISSERVER, {"Core": {}}]
			,'313': [self.RPL_WHOISOPERATOR, {"Core": {}}]
			,'314': [self.RPL_WHOWASUSER, {"Core": {}}]
			,'315': [self.RPL_ENDOFWHO, {"Core": {}}]
			,'317': [self.RPL_WHOISIDLE, {"Core": {}}]
			,'318': [self.RPL_ENDOFWHOIS, {"Core": {}}]
			,'319': [self.RPL_WHOISCHANNELS, {"Core": {}}]
			,'321': [self.RPL_LISTSTART, {"Core": {}}]
			,'322': [self.RPL_LIST, {"Core": {}}]
			,'323': [self.RPL_LISTEND, {"Core": {}}]
			,'324': [self.RPL_CHANNELMODEIS, {"Core": {}}]
			,'331': [self.RPL_NOTOPIC, {"Core": {}}]
			,'332': [self.RPL_TOPIC, {"Core": {}}]
			,'341': [self.RPL_INVITING, {"Core": {}}]
			,'342': [self.RPL_SUMMONING, {"Core": {}}]
			,'351': [self.RPL_VERSION, {"Core": {}}]
			,'352': [self.RPL_WHOREPLY, {"Core": {}}]
			,'353': [self.RPL_NAMREPLY, {"Core": {}}]
			,'364': [self.RPL_LINKS, {"Core": {}}]
			,'365': [self.RPL_ENDOFLINKS, {"Core": {}}]
			,'366': [self.RPL_ENDOFNAMES, {"Core": {}}]
			,'367': [self.RPL_BANLIST, {"Core": {}}]
			,'368': [self.RPL_ENDOFBANLIST, {"Core": {}}]
			,'369': [self.RPL_ENDOFWHOWAS, {"Core": {}}]
			,'371': [self.RPL_INFO, {"Core": {}}]
			,'372': [self.RPL_MOTD, {"Core": {}}]
			,'374': [self.RPL_ENDOFINFO, {"Core": {}}]
			,'375': [self.RPL_MOTDSTART, {"Core": {}}]
			,'376': [self.RPL_ENDOFMOTD, {"Core": {}}]
			,'381': [self.RPL_YOUREOPER, {"Core": {}}]
			,'382': [self.RPL_REHASHING, {"Core": {}}]
			,'391': [self.RPL_TIME, {"Core": {}}]
			,'392': [self.RPL_USERSSTART, {"Core": {}}]
			,'393': [self.RPL_USERS, {"Core": {}}]
			,'394': [self.RPL_ENDOFUSERS, {"Core": {}}]
			,'395': [self.RPL_NOUSERS, {"Core": {}}]

			# ERROR replies.
			,'401': [self.ERR_NOSUCHNICK, {"Core": {}}]
			,'402': [self.ERR_NOSUCHSERVER, {"Core": {}}]
			,'403': [self.ERR_NOSUCHCHANNEL, {"Core": {}}]
			,'404': [self.ERR_CANNOTSENDTOCHAN, {"Core": {}}]
			,'405': [self.ERR_TOOMANYCHANNELS, {"Core": {}}]
			,'406': [self.ERR_WASNOSUCHNICK, {"Core": {}}]
			,'407': [self.ERR_TOOMANYTARGETS, {"Core": {}}]
			,'409': [self.ERR_NOORIGIN, {"Core": {}}]
			,'411': [self.ERR_NORECIPIENT, {"Core": {}}]
			,'412': [self.ERR_NOTEXTTOSEND, {"Core": {}}]
			,'413': [self.ERR_NOTTOPLEVEL, {"Core": {}}]
			,'414': [self.ERR_WILDTOPLEVEL, {"Core": {}}]
			,'421': [self.ERR_UNKNOWNCOMMAND, {"Core": {}}]
			,'422': [self.ERR_NOMOTD, {"Core": {}}]
			,'423': [self.ERR_NOADMININFO, {"Core": {}}]
			,'424': [self.ERR_FILEERROR, {"Core": {}}]
			,'431': [self.ERR_NONICKNAMEGIVEN, {"Core": {}}]
			,'432': [self.ERR_ERRONEUSNICKNAME, {"Core": {}}]
			,'433': [self.ERR_NICKNAMEINUSE, {"Core": {}}]
			,'436': [self.ERR_NICKCOLLISION, {"Core": {}}]
			,'441': [self.ERR_USERNOTINCHANNEL, {"Core": {}}]
			,'442': [self.ERR_NOTONCHANNEL, {"Core": {}}]
			,'443': [self.ERR_USERONCHANNEL, {"Core": {}}]
			,'444': [self.ERR_NOLOGIN, {"Core": {}}]
			,'445': [self.ERR_SOMMUNDISABLED, {"Core": {}}]
			,'446': [self.ERR_USERSDISABLED, {"Core": {}}]
			,'451': [self.ERR_NOTREGISTERED, {"Core": {}}]
			,'461': [self.ERR_NEEDMOREPARAMS, {"Core": {}}]
			,'462': [self.ERR_ALREADYREGISTERED, {"Core": {}}]
			,'463': [self.ERR_NOPERMFORHOST, {"Core": {}}]
			,'464': [self.ERR_PASSWDMISMATCH, {"Core": {}}]
			,'465': [self.ERR_YOUREBANNEDCREEP, {"Core": {}}]
			,'467': [self.ERR_KEYSET, {"Core": {}}]
			,'471': [self.ERR_CHANNELISFULL, {"Core": {}}]
			,'472': [self.ERR_UNKNOWNMODE, {"Core": {}}]
			,'473': [self.ERR_INVITEONLYCHAN, {"Core": {}}]
			,'474': [self.ERR_BANNEDFROMCHAN, {"Core": {}}]
			,'475': [self.ERR_BADCHANNELKEY, {"Core": {}}]
			,'481': [self.ERR_NOPRIVILEGES, {"Core": {}}]
			,'482': [self.ERR_CHANOPRIVSNEEDED, {"Core": {}}]
			,'483': [self.ERR_CANTKILLSERVER, {"Core": {}}]
			,'491': [self.ERR_NOOPERHOST, {"Core": {}}]
			,'501': [self.ERR_UMODEUNKNOWNFLAG, {"Core": {}}]
			,'502': [self.ERR_USERSDONTMATCH, {"Core": {}}]

			# RESERVED Numerals
			,'384': [self.RPL_MYPORTIS, {"Core": {}}]
			,'235': [self.RPL_SERVLISTEND, {"Core": {}}]
			,'209': [self.RPL_TRACECLASS, {"Core": {}}]
			,'466': [self.ERR_YOUWILLBEBANNED, {"Core": {}}]
			,'217': [self.RPL_STATSQLINE, {"Core": {}}]
			,'476': [self.ERR_BADCHANMASK, {"Core": {}}]
			,'231': [self.RPL_SERVICEINFO, {"Core": {}}]
			,'232': [self.RPL_ENDOFSERVICES, {"Core": {}}]
			,'233': [self.RPL_SERVICE, {"Core": {}}]
			,'234': [self.RPL_SERVLIST, {"Core": {}}]
			,'363': [self.RPL_CLOSEEND, {"Core": {}}]
			,'492': [self.ERR_NOSERVICEHOST, {"Core": {}}]
			,'373': [self.RPL_INFOSTART, {"Core": {}}]
			,'361': [self.RPL_KILLDONE, {"Core": {}}]
			,'316': [self.RPL_WHOISCHANOP, {"Core": {}}]
			,'362': [self.RPL_CLOSING, {"Core": {}}]
		}

		self.loadedPlugins = { #PluginName: MainInstance
			}
		self.loadPlugins()

	def onConnect(self, function):
		"""Hook a function to run when connecting."""
		self._onConnect.append(function)

	def userHasAccess(self, hostmask):
		Nick, Ident, Host = re.split("!|@", hostmask)
		if (Nick not in Config.Servers[self.Connection.__name__]['owner']['nicks'] or
			Ident not in Config.Servers[self.Connection.__name__]['owner']['idents'] or
				Host not in Config.Servers[self.Connection.__name__]['owner']['hosts']):
					return False
		return True

	def getPluginList(self):
		if self.Connection.Config['plugins'] is None:
			return []
		files = [f for f in glob.glob("Plugins/*/Main.py")]
		modules = []
		for f in files:
			path = f[8:-3].replace(os.sep, '.')
			if path.split(".")[0] in self.Connection.Config['plugins']:
				modules.append(path)
		return modules

	def loadPlugins(self, m=None):
		modules = self.getPluginList()
		loaded = {}
		for path in modules:
			plugin = path.split('.')[0]
			if m != None and m != plugin:
				continue
			try:
				logger.info("{0}: Trying to import {1}.".format(self.Connection.__name__, plugin))
				loaded[plugin] = importlib.import_module("Plugins.{0}.Main".format(plugin))
				if m != None:
					loaded[plugin] = imp.reload(loaded[plugin])
			except ImportError as e:
				logger.exception("{0}: Error importing '{1}'; Is there a Main.py?".format(self.Connection.__name__, plugin))
			except Exception as e:
				logger.exception("{0}: An Error occured trying to import {1}:".format(self.Connection.__name__, plugin))
		self.initPlugins(loaded)

	def initPlugins(self, loaded):
		for plugin, instance in loaded.items():
			try:
				self.loadedPlugins[plugin] = instance.Main(plugin, self)
				self.loadedPlugins[plugin].Load()
			except Exception as e:
				logger.exception("{0}: Error creating instance of {1}.Main()".format(self.Connection.__name__, plugin))
				if self.loadedPlugins.get(plugin, None) is not None:
					del self.loadedPlugins[plugin]
				continue
		logger.info("{0}: Loaded Plugins!".format(self.Connection.__name__))

	def unLoadPlugins(self, module):
		if self.loadedPlugins.get(module):
			try:
				self.loadedPlugins[module].Unload()
			except Exception as e:
				logger.exception("Error unloading {0}".format(module))
			if self.loadedPlugins.get(module, None) is not None:
				del self.loadedPlugins[module]
		else:
			logger.warn("Trying to unload a nonexistant module")

	def reLoadPlugins(self, data):
		if self.userHasAccess(data[0]) == False:
			return None
		module = data[4]
		self.unLoadPlugins(module)
		self.loadPlugins(m=module)
		self.IRC.say(data[2], "Reloaded {0}!".format(module))

	def hookCommand(self, command, plugin, callbacks):
		# Commands['privmsg'][1]['PluginName'] = {regex: callback}
		if self.Commands[command][1].get(plugin):
			# Prevent multiple instances horribly.
			del self.Commands[command][1][plugin]
		self.Commands[command][1][plugin] = callbacks

	def Shutdown(self, data):
		if self.userHasAccess(data[0]) == False:
			return None
		for Conn in self.Connection.Connections:
			Conn.quitConnection()

	def Parse(self, data):
		data = str(re.sub(Config.Global['unwantedchars'], '', data))
		if data.startswith("PING"):
			return None # blackbox handles PONG replies for us
		elif data.startswith("ERROR"):
			raise IRCError(data) # Oh, look, an error!

		data = data[1:].split()
		if data[1] in list(self.Commands.keys()):
			self.Commands[data[1]][0](data)

	def PRIVMSG(self, data):
		try:
			Nick, Ident, Host = re.split("!|@", data[0])
		except ValueError:
			Server = data[0][1:]

		if data[2] == self.IRC.getnick():
			data[2] = Nick

		commands = []
		# "PRIVMSG" [self.PRIVMSG, {Plugin: {Regex: Callback} } ]
		for Plugin, Commands in self.Commands['PRIVMSG'][1].items():
			for Regex, Callback in Commands.items():
				if re.search(Regex, " ".join(data[3:])[1:]):
					logger.info("Creating thread for function {0}".format(repr(Callback)))
					t = threading.Thread(target=Callback, args=(data,))
					t.daemon = True
					commands.append(t)
		for com in commands:
			com.start()

	def NOTICE(self, data):
		try:
			Nick, Ident, Host = re.split("!|@", data[0])
		except ValueError:
			Server = data[0][1:]
		commands = []
		for Plugin, Commands in self.Commands['NOTICE'][1].items():
			for Regex, Callback in Commands.items():
				if re.search(Regex, " ".join(data[3:])[1:]):
					logger.info("Creating thread for function {0}".format(repr(Callback)))
					t = threading.Thread(target=Callback, args=(data,))
					t.daemon = True
					commands.append(t)
		for com in commands:
			com.start()

	def JOIN(self, data):
		for Plugin, Commands in self.Commands['JOIN'][1].items():
			for Regex, Callback in Commands.items():
				if re.search(Regex, " ".join(data[3:])[1:]):
					logger.info("Calling {0}".format(repr(Callback)))
					Callback(data)

	def PART(self, data):
		pass
	def QUIT(self, data):
		# :user!ident@host QUIT :Reason #Covers /kill too.
		for Plugin, Commands in self.Commands['QUIT'][1].items():
			for Regex, Callback in Commands.items():
				if re.search(Regex, " ".join(data[3:])[1:]):
					logger.info("Calling {0}".format(repr(Callback)))
					Callback(data)

	def KILL(self, data):
		pass
	def MODE(self, data):
		pass
	def NICK(self, data):
		pass

	def KICK(self, data):
		for Plugin, Commands in self.Commands['KICK'][1].items():
			for Regex, Callback in Commands.items():
				if re.search(Regex, " ".join(data[3:])[1:]):
					logger.info("Calling {0}".format(repr(Callback)))
					Callback(data)

	def WALLOPS(self, data):
		pass

	def RPL_TRACELINK(self, data):
		pass
	def RPL_TRACECONNECTING(self, data):
		pass
	def RPL_TRACEHANDSHAKE(self, data):
		pass
	def RPL_TRACEUNKNOWN(self, data):
		pass
	def RPL_TRACEOPERATOR(self, data):
		pass
	def RPL_TRACEUSER(self, data):
		pass
	def RPL_TRACESERVER(self, data):
		pass
	def RPL_TRACENEWTYPE(self, data):
		pass
	def RPL_STATSLINKINFO(self, data):
		pass
	def RPL_STATSCOMMANDS(self, data):
		pass
	def RPL_STATSCLINE(self, data):
		pass
	def RPL_STATSNLINE(self, data):
		pass
	def RPL_STATSILINE(self, data):
		pass
	def RPL_STATSKLINE(self, data):
		pass
	def RPL_STATSYLINE(self, data):
		pass
	def RPL_ENDOFSTATS(self, data):
		pass
	def RPL_UMODEIS(self, data):
		pass
	def RPL_STATSLLINE(self, data):
		pass
	def RPL_STATSUPTIME(self, data):
		pass
	def RPL_STATSOLINE(self, data):
		pass
	def RPL_STATSHLINE(self, data):
		pass
	def RPL_LUSERCLIENT(self, data):
		pass
	def RPL_LUSEROP(self, data):
		pass
	def RPL_LUSERUNKNOWN(self, data):
		pass
	def RPL_LUSERCHANNELS(self, data):
		pass
	def RPL_LUSERME(self, data):
		pass
	def RPL_ADMINME(self, data):
		pass
	def RPL_ADMINLOC1(self, data):
		pass
	def RPL_ADMINLOC2(self, data):
		pass
	def RPL_ADMINEMAIL(self, data):
		pass
	def RPL_TRACELOG(self, data):
		pass
	def RPL_NONE(self, data):
		pass
	def RPL_AWAY(self, data):
		pass
	def RPL_USERHOST(self, data):
		pass
	def RPL_ISON(self, data):
		pass
	def RPL_UNAWAY(self, data):
		pass
	def RPL_NOWAWAY(self, data):
		pass
	def RPL_WHOISUSER(self, data):
		pass
	def RPL_WHOISSERVER(self, data):
		pass
	def RPL_WHOISOPERATOR(self, data):
		pass
	def RPL_WHOWASUSER(self, data):
		pass
	def RPL_ENDOFWHO(self, data):
		pass
	def RPL_WHOISIDLE(self, data):
		pass
	def RPL_ENDOFWHOIS(self, data):
		pass
	def RPL_WHOISCHANNELS(self, data):
		pass
	def RPL_LISTSTART(self, data):
		pass
	def RPL_LIST(self, data):
		pass
	def RPL_LISTEND(self, data):
		pass
	def RPL_CHANNELMODEIS(self, data):
		pass
	def RPL_NOTOPIC(self, data):
		pass
	def RPL_TOPIC(self, data):
		pass
	def RPL_INVITING(self, data):
		pass
	def RPL_SUMMONING(self, data):
		pass
	def RPL_VERSION(self, data):
		pass
	def RPL_WHOREPLY(self, data):
		pass
	def RPL_NAMREPLY(self, data):
		pass
	def RPL_LINKS(self, data):
		pass
	def RPL_ENDOFLINKS(self, data):
		pass
	def RPL_ENDOFNAMES(self, data):
		pass
	def RPL_BANLIST(self, data):
		pass
	def RPL_ENDOFBANLIST(self, data):
		pass
	def RPL_ENDOFWHOWAS(self, data):
		pass
	def RPL_INFO(self, data):
		pass
	def RPL_MOTD(self, data):
		pass
	def RPL_ENDOFINFO(self, data):
		pass
	def RPL_MOTDSTART(self, data):
		pass
	def RPL_ENDOFMOTD(self, data):
		pass
	def RPL_YOUREOPER(self, data):
		pass
	def RPL_REHASHING(self, data):
		pass
	def RPL_TIME(self, data):
		pass
	def RPL_USERSSTART(self, data):
		pass
	def RPL_USERS(self, data):
		pass
	def RPL_ENDOFUSERS(self, data):
		pass
	def RPL_NOUSERS(self, data):
		pass
	def ERR_NOSUCHNICK(self, data):
		pass
	def ERR_NOSUCHSERVER(self, data):
		pass
	def ERR_NOSUCHCHANNEL(self, data):
		pass
	def ERR_CANNOTSENDTOCHAN(self, data):
		pass
	def ERR_TOOMANYCHANNELS(self, data):
		pass
	def ERR_WASNOSUCHNICK(self, data):
		pass
	def ERR_TOOMANYTARGETS(self, data):
		pass
	def ERR_NOORIGIN(self, data):
		pass
	def ERR_NORECIPIENT(self, data):
		pass
	def ERR_NOTEXTTOSEND(self, data):
		pass
	def ERR_NOTTOPLEVEL(self, data):
		pass
	def ERR_WILDTOPLEVEL(self, data):
		pass
	def ERR_UNKNOWNCOMMAND(self, data):
		pass
	def ERR_NOMOTD(self, data):
		pass
	def ERR_NOADMININFO(self, data):
		pass
	def ERR_FILEERROR(self, data):
		pass
	def ERR_NONICKNAMEGIVEN(self, data):
		pass
	def ERR_ERRONEUSNICKNAME(self, data):
		pass
	def ERR_NICKNAMEINUSE(self, data):
		pass
	def ERR_NICKCOLLISION(self, data):
		pass
	def ERR_USERNOTINCHANNEL(self, data):
		pass
	def ERR_NOTONCHANNEL(self, data):
		pass
	def ERR_USERONCHANNEL(self, data):
		pass
	def ERR_NOLOGIN(self, data):
		pass
	def ERR_SOMMUNDISABLED(self, data):
		pass
	def ERR_USERSDISABLED(self, data):
		pass
	def ERR_NOTREGISTERED(self, data):
		pass
	def ERR_NEEDMOREPARAMS(self, data):
		pass
	def ERR_ALREADYREGISTERED(self, data):
		pass
	def ERR_NOPERMFORHOST(self, data):
		pass
	def ERR_PASSWDMISMATCH(self, data):
		pass
	def ERR_YOUREBANNEDCREEP(self, data):
		pass
	def ERR_KEYSET(self, data):
		pass
	def ERR_CHANNELISFULL(self, data):
		pass
	def ERR_UNKNOWNMODE(self, data):
		pass
	def ERR_INVITEONLYCHAN(self, data):
		pass
	def ERR_BANNEDFROMCHAN(self, data):
		pass
	def ERR_BADCHANNELKEY(self, data):
		pass
	def ERR_NOPRIVILEGES(self, data):
		pass
	def ERR_CHANOPRIVSNEEDED(self, data):
		pass
	def ERR_CANTKILLSERVER(self, data):
		pass
	def ERR_NOOPERHOST(self, data):
		pass
	def ERR_UMODEUNKNOWNFLAG(self, data):
		pass
	def ERR_USERSDONTMATCH(self, data):
		pass
	def RPL_MYPORTIS(self, data):
		pass
	def RPL_SERVLISTEND(self, data):
		pass
	def RPL_TRACECLASS(self, data):
		pass
	def ERR_YOUWILLBEBANNED(self, data):
		pass
	def RPL_STATSQLINE(self, data):
		pass
	def ERR_BADCHANMASK(self, data):
		pass
	def RPL_SERVICEINFO(self, data):
		pass
	def RPL_ENDOFSERVICES(self, data):
		pass
	def RPL_SERVICE(self, data):
		pass
	def RPL_SERVLIST(self, data):
		pass
	def RPL_CLOSEEND(self, data):
		pass
	def ERR_NOSERVICEHOST(self, data):
		pass
	def RPL_INFOSTART(self, data):
		pass
	def RPL_KILLDONE(self, data):
		pass
	def RPL_WHOISCHANOP(self, data):
		pass
	def RPL_CLOSING(self, data):
		pass


class Locker(object):
	def __init__(self, Time=None):
		self.Time = Time if Time or Time == 0 and type(Time) == int else 5
		# banhammer would be proud ;-;
		self.Locked = False

	def Lock(self):
		if not self.Locked:
			if self.Time > 0:
				self.Locked = True
				t = threading.Timer(self.Time, self.Unlock, ())
				t.daemon = True
				t.start()
		return self.Locked

	def Unlock(self):
		self.Locked = False
		return self.Locked

