#!/usr/bin/env python
from threading import Thread
from datetime import datetime
import time, re

import Commands
from Services import Users as _U

class Parse():
	def __init__(self, sock=None, allowed=None, nick=None):
		self.sock = sock
		self.allowed = allowed
		self.nickname = nick
		self.Buffer = u''

		self.Users = _U.Users() # Users.Userlist: Storage for Users of each channel. The Key is channel, users are a list.

		self.command = Commands.Commands(parser=self, nick=self.nickname, allowed=self.allowed)
		self._commands = self.command.cmds.keys()

		self.ctcpReplies = {u"\x01VERSION\x01" : "I am WhergBot, A Python based IRC bot."
			,u"\x01TIME\x01" : "The local time here is {0}"
			,u"\x01SOURCE\x01" : "My latest source can be found at https://github.com/Ferus/WhergBot"
			,u"\x01H\x01" : "h"
			}

		self.Actions = {
			u'PRIVMSG': self.Privmsg,
			u'NOTICE': self.Notice,
			u'WALLOPS': self.Wallops,
			u'INVITE': self.Invited,
			u'TOPIC': self.TopicChange,
			u'KICK': self.Kicked,
			u'JOIN': self.Joined,
			u'PART': self.Parted,
			u'QUIT': self.Quitted,
			u'NICK': self.Nickchange,
			u'MODE': self.Modechange,
			u'KILL': self.Killed,
			u'001': self.Welcome,
			u'002': self.NormalMsg,
			u'003': self.NormalMsg,
			u'004': self.NormalMsg,
			u'005': self.IgnoreLine,
			u'008': self.IgnoreLine,
			u'251': self.NormalMsg,
			u'252': self.NormalMsg,
			u'253': self.NormalMsg,
			u'254': self.NormalMsg,
			u'255': self.NormalMsg,
			u'265': self.NormalMsg,
			u'266': self.NormalMsg,
			u'331': self.NoTopic,
			u'332': self.Topic,
			u'333': self.TopicTime,
			u'352': self.Who,
			u'353': self.Names,
			u'366': self.IgnoreLine,
			u'372': self.MOTD,
			u'375': self.MOTD,
			u'376': self.MOTD,
			u'381': self.NormalMsg,
			u'404': self.BannedVoice,
			u'422': self.NormalMsg,
			u'451': self.NormalMsg,
			u'474': self.Banned,

			u':Closing' : self.IgnoreLine, # HAX
			}

	def Main(self, msg):
		'''Main Parser, Here we take raw data, and split at \r\n.'''
		self.Buffer += msg
		msg = re.split(u"\r|\r\n|\n", self.Buffer)
		#	...this should really catch the end of the buffer if it didnt recv all of it. :|
		#	somehow it derps.
		self.Buffer = u''

		for line in msg:
			if not line:
				continue

			line = re.sub(u"\x03(?:[0-9]{1,2})?(?:,[0-9]{1,2})?|\x02|\x07", u"", line)
			#	Unwanted Chars, like color, bold, underline, etc.

			line = line.lstrip(":")

			if line.split()[1] in self.Actions.keys():
				self.Actions[line.split()[1]](line)

			elif line.startswith("PING"):
				print(u"* [IRC] Ping from {0}, ponging back.".format(line.split(u":")[1]))

			else:
				print(u"* [DERP] {0}".format(line.split()))

	def Privmsg(self, msg):
		'''Parse for commands. Etc.'''
		tmp = msg.split()
		try:
			Nick, Host = tmp[0].split(u"!")
			Action = tmp[1]
			Text = u" ".join(tmp[3:])[1:]
			Cmd = tmp[3][1:]
			if tmp[2] == self.nickname:
				Location = tmp[0].split(u"!")[0]
			else:
				Location = tmp[2]
			Msg = [Nick, Host, Action, Location, Text, Cmd]
		except Exception, e:
			print("* [Privmsg Error] {0}".format(repr(e)))

		if Nick == Location:
			Location = self.nickname

		try:
			if Text.startswith(u"\x01"):
				if Cmd in self.ctcpReplies.keys():
					'''The message received was a CTCP'''
					if Cmd.strip(u"\x01") == u'TIME':
						ti = self.ctcpReplies[Cmd].format(time.strftime(u"%c", time.localtime()))
						t = Thread(target=self.CTCP(Cmd.strip(u"\x01"), Nick, ti))
						t.daemon = True
						t.start()

					else:
						t = Thread(target=self.CTCP(Cmd.strip(u"\x01"), Nick, self.ctcpReplies[Cmd]))
						t.daemon = True
						t.start()
				else:
					if Cmd.strip(u"\x01") == u'ACTION':
						act = u" ".join(Text.strip("\x01").split()[1:])
						print(u"* [Privmsg] [{0}] * {1} {2}".format(Location, Nick, act))

			elif Cmd == u'\x01DCC':
				'''I probably won't add dcc support.'''
				print(u"* [DCC] {0} request from {1}. Since DCC isnt implemented yet, we are just going to 'ignore' this.".format(Text.split()[1], Nick))

			else:
				'''
				If a command is called, check the hostname and access level of the person who called it,
				and if they have access, execute the command. Regex based commands too. :)
				'''
				print(u"* [Privmsg] [{0}] <{1}> {2}".format(Location, Nick, Text))
				if self.command.Locker.Locked and Nick != self.allowed.Owner[0]:
					self.sock.notice(Nick, "Sorry but I'm locked bro.")
					return None
				for comm in self._commands: #Loop through every one.
					if re.search(comm+u"(\s|$)", Text): #If we match a command
						check = self.allowed.levelCheck(Nick)[1] #Start an access check
						if check[1] <= self.command.cmds[comm][1]: #Check access level
							if self.command.cmds[comm][2]: #Is a hostcheck needed?
								if Host == check[0]: #Hostcheck
									t = Thread(target=(self.command.cmds[comm])[0](Msg, self.sock, self.Users, self.allowed))
									t.daemon = True
									t.start()
								else: #Failed the hostcheck
									self.sock.notice(Nick, u"You do not have the required authority to use this command.")
							else: #Passes access, but no hostcheck needed
								t = Thread(target=(self.command.cmds[comm])[0](Msg, self.sock, self.Users, self.allowed))
								t.daemon = True
								t.start()
						else: #Doesnt pass access.
							pass
					#else: #Debugging.
					#	print(str(re.findall(comm+u"(\s|$)", Text)) +" "+ comm+u"(\s|$)")
		except Exception, e:
			print("* [Privmsg Error] {0}".format(repr(e)))

	def Notice(self, msg):
		msg = msg.split()
		try:
			Nick = msg[0].split("!")[0]
		except:
			Nick = msg[0]
		Text = u" ".join(msg[3:]).lstrip(u":")
		print(u"* [Notice] <{0}> {1}".format(Nick, Text))

	def Wallops(self, msg):
		msg = msg.split()
		person, host = msg[0].split("!")
		print(u"* [WALLOPS] <{0} ({1})> {2}".format(person, host, u" ".join(msg[2:])[1:]))

	def Invited(self, msg):
		'''Join a channel we were invited to if the person's hostname is defined in allowed.'''
		msg = msg.split()
		try:
			person, host = msg[0].split("!")
			print(u"* [IRC] Invited to {0}, by {1}. Attempting to join.".format(chan, person))
			if self.allowed.db[person][0] == host:
				chan = msg[3][1:]
				self.sock.join(chan)
		except:
			pass

	def Kicked(self, msg):
		msg = msg.split()
		if msg[3] == self.nickname:
			print(u"* [IRC] Kicked from {0} by {1} ({2}). Attempting to Auto-Rejoin.".format(msg[2], msg[0].split(u"!")[0], u" ".join(msg[4:])[1:]))
			self.sock.join(msg[2])
		else:
			print(u"* [IRC] {0} was kicked from {1} by {2}; Reason ({3})".format(msg[3], msg[2], msg[0].split(u"!")[0], u" ".join(msg[4:])[1:]))

	def Joined(self, msg):
		'''Someone joined, add them to allowed, with level 5 access, no hostname, and add them to the channel users list.'''
		msg = msg.split()
		person, host = msg[0].split(u"!")
		chan = msg[2].strip(u":")
		print(u"* [IRC] {0} ({1}) joined {2}.".format(person, host, chan))
		try:
			if person not in self.allowed.keys:
				self.allowed.db[person] = [None, 5]
			self.Users.Userlist[chan].append(person)
		except:
			pass

	def Parted(self, msg):
		msg = msg.split()
		'''Someone parted a channel, remove them from the channel users list.'''
		person, host = msg[0].split("!")
		print(u"* [IRC] {0} ({1}) parted {2}.".format(person, host, msg[2]))
		try:
			self.Users.Userlist[msg[2]].remove(person)
		except:
			pass

	def Quitted(self, msg):
		msg = msg.split()
		person, host = msg[0].split(u"!")
		print(u"* [IRC] {0} ({1}) has quit.".format(person, host))
		try:
			for chan in self.Users.Userlist.keys():
				if person in self.Users.Userlist[chan]:
					self.Users.Userlist[chan].remove(person)
		except:
			pass

	def Nickchange(self, msg):
		msg = msg.split()
		person, host = msg[0].split(u"!")
		new = msg[2][1:]
		print(u"* [IRC] {0} has changed nick to {1}.".format(person, new))
		try:
			for chan in self.Users.Userlist.keys():
				if person in self.Users.Userlist[chan]:
					self.Users.Userlist[chan].remove(person)
					self.Users.Userlist[chan].append(new)
			if new not in self.allowed.keys:
				self.allowed.db[new] = [None, 5]
		except:
			pass

	def Killed(self, msg):
		msg = msg.split()
		print(u"* [IRC] Oper {0} ({1}) KILL'd {2}; Reason: {3}".format(msg[0].split('!')[0], msg[0].split('!')[1], msg[2], msg[-1]))

	def TopicChange(self, msg):
		msg = msg.split()
		print(u"* [IRC] {0} has changed the topic of {1} to '{2}'".format(msg[0].split(u"!")[0], msg[2], u" ".join(msg[3:])[1:]))

	def Modechange(self, msg):
		msg = msg.split()
		try:
			person, host = msg[0].split(u"!")
			if len(msg[3]) > 2: #Multiple modes set
				print(u"* [IRC] {0} ({1}) set modes {2} on channel {3}.".format(person, host, u" ".join(msg[3:]), msg[2]))
			else:
				print(u"* [IRC] {0} ({1}) set mode {2} on channel {3}.".format(person, host, u" ".join(msg[3:]), msg[2]))
		except:
			print(u"* [IRC] Modes {0} set.".format(msg[3].split(":")[1]))

	def CTCP(self, ctcp, location, message):
		'''CTCP'd. Lets respond.'''
		self.sock.send(u"NOTICE {0} :{1}".format(location, message))
		print(u"* [CTCP {0} from {1}] Replying with: '{2}'".format(ctcp, location, message))

	def NoTopic(self, msg):
		msg = msg.split()
		print(u"* [IRC] There is no topic set for {0}".format(msg[3]))

	def Topic(self, msg):
		msg = msg.split()
		print(u"* [IRC] Topic for {0} set to {1}".format(msg[3] , u" ".join(msg[4:])[1:]))

	def TopicTime(self, msg):
		msg = msg.split()
		print(datetime.fromtimestamp(int(msg[5])).strftime(u"* [IRC] Topic for {0} set by {1} at %c".format(msg[3], msg[4])))

	def Who(self, msg):
		msg = msg.split()
		person, host = msg[7], msg[4]+"@"+msg[5]
		print(u"* [IRC] {0} has Ident/Host of '{1}' and Realname of '{2}'.".format(person, host, u" ".join(msg[10:])))
		if u"*" in msg[8]:
			print(u"* [IRC] {0} is an IRC Operator on {1}.".format(person, msg[6]))
		if u'H' in msg[8]:
			print(u"* [IRC] {0} is currently available.".format(person))
		if u'G' in msg[8]:
			print(u"* [IRC] {0} is currently away.".format(person))

	def Names(self, msg):
		msg = msg.split()
		nameslist = []
		for x in msg[5:]:
			x = re.sub(u"[:|~|&|@|%|+]", u"", x)
			nameslist.append(x)
			if x not in self.allowed.db.keys():
				self.allowed.db[x] = [None, 5]
		self.Users.Userlist[msg[4]] = nameslist
		print(u"* [IRC] Users on {0}: {1}".format(msg[4], u" ".join(nameslist)))

	def MOTD(self, msg):
		print(u"* [MOTD]{0}".format(msg.split(self.nickname)[1]))

	def Banned(self, msg):
		msg = msg.split()
		print(u"* [IRC] Cannot join {0}, Banned (+b).".format(msg[3]))

	def BannedVoice(self, msg):
		msg = msg.split()
		print(u"* [IRC] Cannot speak in {0}; Banned/No voice.".format(msg[3]))

	def Welcome(self, msg):
		msg = msg.split()
		print(u"* [IRC] {0}, {1}".format(u" ".join(msg[3:-1])[1:], msg[2]))

	def NormalMsg(self, msg):
		msg = msg.split()
		print(u"* [IRC] {0}".format(u" ".join(msg[3:]).lstrip(u":")))

	def IgnoreLine(self, msg):
		pass