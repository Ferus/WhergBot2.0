#!/usr/bin/env python
import re

# Plugin that auto-accepts users' requested vHosts
# with a blacklist to deny certain phrases.
# (Not yet) tested on UnrealIRCd with Anope Services.


# regexs to block, we only re.match() the items in
# the blacklist, meaning these are not exact and
# assume a wildcard on either side unless specifying
# ^ and $ in the blacklist

# opers can still override by manually setting
# vhosts, if issues arise, with /msg HostServ set

# Future changes; if any:
# HostServ's nick should be a setting
# Channel name for Services should be a setting

blacklist = ["\.?datnode\.?" # datnode
	,"\.?admin\.?" # admin
	,"\.?op(?=\.)" # op.
	,"\.?mod(?=\.)" # mod.
	,"\.?services\.?" # services
	,"\.?operator\.?" # operator
	,"\.?system\.?" # system
	,"\.?sysadmin\.?" # sysadmin
	,"\.?sysop\.?" # sysop
	,"\.?netop\.?" # netop
	,"\.?kimmo\.?" # kimmo
	]
regex = "New vHost Requested by ([-.\w\d()[\]{}^].+)$"
nregex = "#\d+ Nick:([-.\w\d()[\]{}^].+), vhost:([\w.]+) .*$"

class Main(object):
	def __init__(self, Name, Parser):
		self.__name__ = Name
		self.Parser = Parser
		self.IRC = self.Parser.IRC

	def message(self, data):
		self.IRC.say("HostServ", "Waiting")

	def notice(self, data):
		d = " ".join(data[3:])[1:]
		nick, vhost = re.match(nregex, d).groups()
		for bl in blacklist:
			if re.search(bl, vhost):
				self.IRC.say("HostServ", "reject {0}".format(nick))
				self.IRC.say("#services", "Rejected the vHost of {0} (\x02{1}\x02) because it matched the following regex: {2}".format(nick, vhost, bl))
				self.IRC.say(nick, "Your vHost request was \x02DENIED\x02 because it contains a blacklisted word or phrase.")
				self.IRC.say(nick, "If you feel this was in error, please PM an Oper with this message.")
				return None

		self.IRC.say("HostServ", "activate {0}".format(nick))
		self.IRC.say("#services", "Activated vHost (\x02{0}\x02) of user \x02{1}\x02".format(vhost, nick))
		self.IRC.say(nick, "Your vHost request was \x02ACCEPTED\x02!")
		self.IRC.say(nick, "Please use \"\x02/msg HostServ ON\x02\" to activate it.")

	def Load(self):
		self.Parser.hookCommand("PRIVMSG", self.__name__, {regex: self.message})
		self.Parser.hookCommand("NOTICE", self.__name__, {nregex: self.notice})

	def Unload(self):
		del self.Parser.Commands['PRIVMSG'][1][self.__name__]
