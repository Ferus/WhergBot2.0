#!/usr/bin/env python
import os
import sys
import imp
import glob
import re

from threading import Timer
from time import strftime

from blackbox.blackbox import IRCError
import Config

class Parser(object):
	def __init__(self, Connection):
		self.Connection = Connection
		self.IRC = self.Connection.IRC
		self._onConnect = []

		self.Commands = {
			# NON-NUMERICAL responses
			"PRIVMSG": [self.PRIVMSG, {'^@quit( .*?)?$': self.Shutdown
				,'^@reload \w+$': self.reLoadPlugins
				,'^@load \w+$': self.reLoadPlugins # loadPlugins() handles all
				,'^@unload \w+$': self.unLoadPlugins
				}
			] # [Regex, Callback]
			,"NOTICE": [self.NOTICE, {}]
			,"JOIN": [self.JOIN, {}]
			,"PART": [self.PART, {}]
			,"QUIT": [self.QUIT, {}]
			,"KILL": [self.KILL, {}]
			,"MODE": [self.MODE, {}]
			,"NICK": [self.NICK, {}]
			,"WALLOPS": [self.WALLOPS, {}]

			# COMMAND responses
			,'200': [self.RPL_TRACELINK, {}]
			,'201': [self.RPL_TRACECONNECTING, {}]
			,'202': [self.RPL_TRACEHANDSHAKE, {}]
			,'203': [self.RPL_TRACEUNKNOWN, {}]
			,'204': [self.RPL_TRACEOPERATOR, {}]
			,'205': [self.RPL_TRACEUSER, {}]
			,'206': [self.RPL_TRACESERVER, {}]
			,'208': [self.RPL_TRACENEWTYPE, {}]
			,'211': [self.RPL_STATSLINKINFO, {}]
			,'212': [self.RPL_STATSCOMMANDS, {}]
			,'213': [self.RPL_STATSCLINE, {}]
			,'214': [self.RPL_STATSNLINE, {}]
			,'215': [self.RPL_STATSILINE, {}]
			,'216': [self.RPL_STATSKLINE, {}]
			,'218': [self.RPL_STATSYLINE, {}]
			,'219': [self.RPL_ENDOFSTATS, {}]
			,'221': [self.RPL_UMODEIS, {}]
			,'241': [self.RPL_STATSLLINE, {}]
			,'242': [self.RPL_STATSUPTIME, {}]
			,'243': [self.RPL_STATSOLINE, {}]
			,'244': [self.RPL_STATSHLINE, {}]
			,'251': [self.RPL_LUSERCLIENT, {}]
			,'252': [self.RPL_LUSEROP, {}]
			,'253': [self.RPL_LUSERUNKNOWN, {}]
			,'254': [self.RPL_LUSERCHANNELS, {}]
			,'255': [self.RPL_LUSERME, {}]
			,'256': [self.RPL_ADMINME, {}]
			,'257': [self.RPL_ADMINLOC1, {}]
			,'258': [self.RPL_ADMINLOC2, {}]
			,'259': [self.RPL_ADMINEMAIL, {}]
			,'261': [self.RPL_TRACELOG, {}]
			,'300': [self.RPL_NONE, {}]
			,'301': [self.RPL_AWAY, {}]
			,'302': [self.RPL_USERHOST, {}]
			,'303': [self.RPL_ISON, {}]
			,'305': [self.RPL_UNAWAY, {}]
			,'306': [self.RPL_NOWAWAY, {}]
			,'311': [self.RPL_WHOISUSER, {}]
			,'312': [self.RPL_WHOISSERVER, {}]
			,'313': [self.RPL_WHOISOPERATOR, {}]
			,'314': [self.RPL_WHOWASUSER, {}]
			,'315': [self.RPL_ENDOFWHO, {}]
			,'317': [self.RPL_WHOISIDLE, {}]
			,'318': [self.RPL_ENDOFWHOIS, {}]
			,'319': [self.RPL_WHOISCHANNELS, {}]
			,'321': [self.RPL_LISTSTART, {}]
			,'322': [self.RPL_LIST, {}]
			,'323': [self.RPL_LISTEND, {}]
			,'324': [self.RPL_CHANNELMODEIS, {}]
			,'331': [self.RPL_NOTOPIC, {}]
			,'332': [self.RPL_TOPIC, {}]
			,'341': [self.RPL_INVITING, {}]
			,'342': [self.RPL_SUMMONING, {}]
			,'351': [self.RPL_VERSION, {}]
			,'352': [self.RPL_WHOREPLY, {}]
			,'353': [self.RPL_NAMREPLY, {}]
			,'364': [self.RPL_LINKS, {}]
			,'365': [self.RPL_ENDOFLINKS, {}]
			,'366': [self.RPL_ENDOFNAMES, {}]
			,'367': [self.RPL_BANLIST, {}]
			,'368': [self.RPL_ENDOFBANLIST, {}]
			,'369': [self.RPL_ENDOFWHOWAS, {}]
			,'371': [self.RPL_INFO, {}]
			,'372': [self.RPL_MOTD, {}]
			,'374': [self.RPL_ENDOFINFO, {}]
			,'375': [self.RPL_MOTDSTART, {}]
			,'376': [self.RPL_ENDOFMOTD, {}]
			,'381': [self.RPL_YOUREOPER, {}]
			,'382': [self.RPL_REHASHING, {}]
			,'391': [self.RPL_TIME, {}]
			,'392': [self.RPL_USERSSTART, {}]
			,'393': [self.RPL_USERS, {}]
			,'394': [self.RPL_ENDOFUSERS, {}]
			,'395': [self.RPL_NOUSERS, {}]

			# ERROR replies.
			,'401': [self.ERR_NOSUCHNICK, {}]
			,'402': [self.ERR_NOSUCHSERVER, {}]
			,'403': [self.ERR_NOSUCHCHANNEL, {}]
			,'404': [self.ERR_CANNOTSENDTOCHAN, {}]
			,'405': [self.ERR_TOOMANYCHANNELS, {}]
			,'406': [self.ERR_WASNOSUCHNICK, {}]
			,'407': [self.ERR_TOOMANYTARGETS, {}]
			,'409': [self.ERR_NOORIGIN, {}]
			,'411': [self.ERR_NORECIPIENT, {}]
			,'412': [self.ERR_NOTEXTTOSEND, {}]
			,'413': [self.ERR_NOTTOPLEVEL, {}]
			,'414': [self.ERR_WILDTOPLEVEL, {}]
			,'421': [self.ERR_UNKNOWNCOMMAND, {}]
			,'422': [self.ERR_NOMOTD, {}]
			,'423': [self.ERR_NOADMININFO, {}]
			,'424': [self.ERR_FILEERROR, {}]
			,'431': [self.ERR_NONICKNAMEGIVEN, {}]
			,'432': [self.ERR_ERRONEUSNICKNAME, {}]
			,'433': [self.ERR_NICKNAMEINUSE, {}]
			,'436': [self.ERR_NICKCOLLISION, {}]
			,'441': [self.ERR_USERNOTINCHANNEL, {}]
			,'442': [self.ERR_NOTONCHANNEL, {}]
			,'443': [self.ERR_USERONCHANNEL, {}]
			,'444': [self.ERR_NOLOGIN, {}]
			,'445': [self.ERR_SOMMUNDISABLED, {}]
			,'446': [self.ERR_USERSDISABLED, {}]
			,'451': [self.ERR_NOTREGISTERED, {}]
			,'461': [self.ERR_NEEDMOREPARAMS, {}]
			,'462': [self.ERR_ALREADYREGISTERED, {}]
			,'463': [self.ERR_NOPERMFORHOST, {}]
			,'464': [self.ERR_PASSWDMISMATCH, {}]
			,'465': [self.ERR_YOUREBANNEDCREEP, {}]
			,'467': [self.ERR_KEYSET, {}]
			,'471': [self.ERR_CHANNELISFULL, {}]
			,'472': [self.ERR_UNKNOWNMODE, {}]
			,'473': [self.ERR_INVITEONLYCHAN, {}]
			,'474': [self.ERR_BANNEDFROMCHAN, {}]
			,'475': [self.ERR_BADCHANNELKEY, {}]
			,'481': [self.ERR_NOPRIVILEGES, {}]
			,'482': [self.ERR_CHANOPRIVSNEEDED, {}]
			,'483': [self.ERR_CANTKILLSERVER, {}]
			,'491': [self.ERR_NOOPERHOST, {}]
			,'501': [self.ERR_UMODEUNKNOWNFLAG, {}]
			,'502': [self.ERR_USERSDONTMATCH, {}]

			# RESERVED Numerals
			,'384': [self.RPL_MYPORTIS, {}]
			,'235': [self.RPL_SERVLISTEND, {}]
			,'209': [self.RPL_TRACECLASS, {}]
			,'466': [self.ERR_YOUWILLBEBANNED, {}]
			,'217': [self.RPL_STATSQLINE, {}]
			,'476': [self.ERR_BADCHANMASK, {}]
			,'231': [self.RPL_SERVICEINFO, {}]
			,'232': [self.RPL_ENDOFSERVICES, {}]
			,'233': [self.RPL_SERVICE, {}]
			,'234': [self.RPL_SERVLIST, {}]
			,'363': [self.RPL_CLOSEEND, {}]
			,'492': [self.ERR_NOSERVICEHOST, {}]
			,'373': [self.RPL_INFOSTART, {}]
			,'361': [self.RPL_KILLDONE, {}]
			,'316': [self.RPL_WHOISCHANOP, {}]
			,'362': [self.RPL_CLOSING, {}]
		}

		self.loadedPlugins = {
			#PluginName: [PluginInstance, MainInstance, ConfigInstance, LoadFunction, UnloadFunction, ReloadFunction]
		}
		self.loadPlugins()
	
	def onConnect(self, function):
		"""Hook a function to run when connecting."""
		self._onConnect.append(function)

	def getPluginList(self):
		files = [f for f in glob.glob("Plugins/*/Main.py")]
		modules = []
		for f in files:
			path = f[8:-3].replace(os.sep, '.')
			modules.append(path)
		return modules
	
	def loadPlugins(self, data=None):
		modules = self.getPluginList()

		loaded = {}
		for path in modules:
			module = path.split('.')[0]
			try:
				print("{0} {1}: Trying to import {2}.".format(strftime(Config.Global['timeformat']), self.Connection.__name__, module))
				loaded[module] = __import__("Plugins.{0}.Main".format(module), {}, {}, [module])
			except ImportError as e:
				print("{0} {1}: Error importing '{2}'; Is there a Main.py?".format(strftime(Config.Global['timeformat']), self.Connection.__name__, module))
				print(repr(e))
			except Exception, e:
				print("{0} {1}: An Error occured trying to import {2}:".format(strftime(Config.Global['timeformat']), self.Connection.__name__, module))
				print("{0} {1}: {2}".format(strftime(Config.Global['timeformat']), self.Connection.__name__, repr(e)))
		try:
			for plugin, instance in loaded.items():
				self.loadedPlugins[plugin] = [instance, instance.Main(plugin, self)]
				self.loadedPlugins[plugin][1].Load()
			if data:
				self.IRC.say(data[2], "Loaded Plugin!")
			else:
				print("Loaded Plugins!")
		except Exception, e:
			del self.loadedPlugins[plugin]
			print("{0} {1}: Error: {2}".format(strftime(Config.Global['timeformat']), self.Connection.__name__, repr(e)))
			if data:
				self.IRC.say(data[2], "Error: {0}".format(repr(e)))
			else:
				print("Error: {0}".format(repr(e)))
	
	def unLoadPlugins(self, data):
		Nick, Ident, Host = re.split("!|@", data[0])
		if (Nick not in Config.Global['owner']['nicks'] or
			Ident not in Config.Global['owner']['idents'] or
				Host not in Config.Global['owner']['hosts']):
					return None
		module = data[4]
		try:
			self.loadedPlugins[module][1].Unload()
			self.IRC.say(data[2], "Unloaded {0}".format(module))
		except KeyError:
			pass
		except Exception, e:
			self.IRC.say(data[2], repr(e))
	
	def reLoadPlugins(self, data):
		module = data[4]
		self.unLoadPlugins(data)
		modules = self.getPluginList()
		loaded = {}
		for path in modules:
			_module = path.split('.')[0]
			if module != _module:
				continue
			try:
				print("{0} {1}: Trying to import {2}.".format(strftime(Config.Global['timeformat']), self.Connection.__name__, module))
				imp.reload(sys.modules["Plugins.{0}.Settings".format(module)])
				loaded[module] = imp.reload(sys.modules["Plugins.{0}.Main".format(module)])
			except KeyError:
				try:
					loaded[module] = __import__("Plugins.{0}.Main".format(module), {}, {}, [module])
				except ImportError as e:
					self.IRC.say(data[2], repr(e))
				except Exception as e:
					self.IRC.say(data[2], repr(e))
		try:
			for plugin, instance in loaded.items():
				self.loadedPlugins[plugin] = [instance, instance.Main(plugin, self)]
				self.loadedPlugins[plugin][1].Load()
			self.IRC.say(data[2], "Reloaded Plugin!")
		except Exception, e:
			del self.loadedPlugins[plugin]
			print("{0} {1}: Error: {2}".format(strftime(Config.Global['timeformat']), self.Connection.__name__, repr(e)))
			self.IRC.say(data[2], "Error: {0}".format(repr(e)))
	
	def hookCommand(self, command, regex, callback):
		self.Commands[command][1][regex] = callback
	
	def Shutdown(self, data):
		Nick, Ident, Host = re.split("!|@", data[0])
		if (Nick not in Config.Global['owner']['nicks'] or
			Ident not in Config.Global['owner']['idents'] or
				Host not in Config.Global['owner']['hosts']):
					return None

		for Conn in self.Connection.Connections:
			Conn.quitConnection()
	
	def Parse(self, data):
		data = re.sub(Config.Global['unwantedchars'], '', data)
		print("{0} {1}: {2}".format(strftime(Config.Global['timeformat']), self.Connection.__name__, data))
		if data.startswith("PING"):
			return None # blackbox handles PONG replies for us
		elif data.startswith("ERROR"):
			raise IRCError(data) # Oh, look, an error!
		
		data = data[1:].split()
		if data[1] in self.Commands.keys():
			self.Commands[data[1]][0](data)
		

	def PRIVMSG(self, data):
		try:
			Nick, Ident, Host = re.split("!|@", data[0])
		except ValueError:
			Server = data[0][1:]

		if data[2] == Config.Servers[self.Connection.__name__]['nick']: # This is a PM
			data[2] = Nick

		for k, v in self.Commands['PRIVMSG'][1].items():
			if re.search(k, " ".join(data[3:])[1:]):
				v(data)

	def NOTICE(self, data):
		try:
			Nick, Ident, Host = re.split("!|@", data[0])
		except ValueError:
			Server = data[0][1:]

		for k, v in self.Commands['NOTICE'][1].items():
			if re.search(k, " ".join(data[3:])[1:]):
				v(data)

	def JOIN(self, data):
		for k, v in self.Commands['JOIN'][1].items():
			v(data)
	def PART(self, data):
		pass
	def QUIT(self, data):
		# :user!ident@host QUIT :Reason #Covers /kill too.
		for k, v in self.Commands['QUIT'][1].items():
			if re.search(k, " ".join(data)):
				v(data)

	def KILL(self, data):
		pass
	def MODE(self, data):
		pass
	def NICK(self, data):
		pass
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
				t = Timer(self.Time, self.Unlock, ())
				t.daemon = True
				t.start()
		return self.Locked

	def Unlock(self):
		self.Locked = False
		return self.Locked
