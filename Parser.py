#!/usr/bin/python2
#Global Imports
from threading import Thread
from datetime import datetime
import time, re

#Local Imports
import Commands
from Services import Users as _U

class Parse():
	def __init__(self, sock=None, allowed=None, nick=None):
		self.sock = sock
		self.allowed = allowed	
		self.nickname = nick
		self.Buffer = ''

		self.Users = _U.Users() # Users.Userlist: Storage for Users of each channel. The Key is channel, users are a list.
		
		self.command = Commands.Commands(parser=self, nick=self.nickname, allowed=self.allowed)
		self._commands = self.command.cmds.keys()

		self.ctcpReplies = {"\x01VERSION\x01" : "I am WhergBot, A Python based IRC bot.",
			"\x01TIME\x01" : "The local time here is {0}",
			"\x01SOURCE\x01" : "My latest source can be found at https://github.com/Ferus/WhergBot",
			}

							
		self.Actions = {
			'PRIVMSG': self.Privmsg,
			'NOTICE': self.Notice,
			'INVITE': self.Invited,
			'KICK': self.Kicked,
			'JOIN': self.Joined,
			'PART': self.Parted,
			'QUIT': self.Quitted,
			'NICK': self.Nickchange,
			'MODE': self.Modechange,
			'001': self.Welcome,
			'002': self._Welcome,
			'003': self._Welcome,
			'005': self.IgnoreLine,
			'251': self.UserCount,
			'331': self.NoTopic,
			'332': self.Topic,
			'333': self.TopicTime,
			'352': self.Who,
			'353': self.Names,
			'366': self.IgnoreLine,
			'372': self.MOTD,
			'376': self.MOTD,
			'404': self.BannedVoice,
			'474': self.Banned,
			}
			
	def Main(self, msg):
		'''Main Parser, Here we take raw data, and split at \r\n.'''
		self.Buffer += msg
		msg = self.Buffer.split('\r')
		self.Buffer = msg.pop()

		for line in msg:
			if line.startswith("\n"):
				line = line.strip("\n")
			if line.startswith(":"):
				line = line[1:]
			line = line.split()
			if line[1] in self.Actions.keys():
				self.Actions[line[1]](line)

			elif line[7] == 'KILL': #lolhax
				print("* [IRC] {0} killed by oper {1}. Reason: {2}".format(line[10], line[12], " ".join(line[15:])))
			else:
				print line

	
	def Privmsg(self, msg):
		'''Parse for commands. Etc.'''
		tmp = msg
		msg = " ".join(msg)
		try:
			Nick, Host = tmp[0].split("!")
			Action = tmp[1]
			Text = " ".join(tmp[3:])[1:]
			Cmd = tmp[3][1:]
			if tmp[2] == self.nickname:
				Location = tmp[0].split("!")[0]
			else:
				Location = tmp[2]
			Msg = [Nick, Host, Action, Location, Text, Cmd]
			
			if Nick == Location:
				Location = self.nickname
						
			if Text.startswith("\x01"):
				if Cmd in self.ctcpReplies.keys():
					'''The message received was a CTCP'''
					print("* [CTCP] {0}".format(Cmd.strip("\x01")))
					if Cmd.strip("\x01") == 'TIME':
						ti = self.ctcpReplies[Cmd].format(time.strftime("%c", time.localtime()))
						t = Thread(target=self.CTCP(Cmd.strip("\x01"), Nick, ti))
						t.daemon = True																			
						t.start()						
						
					else:
						t = Thread(target=self.CTCP(Cmd.strip("\x01"), Nick, self.ctcpReplies[Cmd]))
						t.daemon = True																			
						t.start()
				else:
					if Cmd.strip("\x01") == 'ACTION':
						act = " ".join(Text.strip("\x01").split()[1:])
						print("* [Privmsg] [{0}] * {1} {2}".format(Location, Nick, act))
						
			elif Cmd == 'DCC':
				'''I probably won't add dcc support.'''
				print("* [DCC] {0} request from {1}. Since DCC isnt implemented yet, we are just going to 'ignore' this.".format(Text.split()[1], Nick))
						
			else:
				'''
				If a command is called, check the hostname and access level of the person who called it, 
				and if they have access, execute the command. Regex based commands too. :)
				'''
				print("* [Privmsg] [{0}] <{1}> {2}".format(Location, Nick, Text))
				for comm in self._commands: #Loop through every one.
					if re.search(comm, Text): #If we match a command
						check = self.allowed.levelCheck(Nick)[1] #Start an access check
						if check[1] <= self.command.cmds[comm][1]: #Check access level
							if self.command.cmds[comm][2]: #Is a hostcheck needed?
								if Host == check[0]: #Hostcheck
									t = Thread(target=(self.command.cmds[comm])[0](Msg, self.sock, self.Users, self.allowed))
									t.daemon = True
									t.start()
								else: #Failed the hostcheck
									self.sock.send("NOTICE {0} :{1}".format(Nick, "You do not have the required authority to use this command."))
							else: #Passes access, but no hostcheck needed
								t = Thread(target=(self.command.cmds[comm])[0](Msg, self.sock, self.Users, self.allowed))
								t.daemon = True
								t.start()
						else: #Doesnt pass access.
							pass
		except Exception, e:
			print("* [Privmsg] Error")
			print(repr(e))
			
	def Notice(self, msg):
		try:
			Nick = msg[0].split("!")[0]
			if Nick.startswith(":"):
				Nick = Nick[1:]
		except:
			Nick = msg[0]
		Text = " ".join(msg[3:])
		if Text.startswith(":"):
			Text = Text[1:]
		print("* [Notice] <{0}> {1}".format(Nick, Text))
	
	def Invited(self, msg):
		'''Join a channel we were invited to if the person's hostname is defined in allowed.'''
		try:
			person, host = msg[0].split("!")
			if self.allowed.db[person][0] == host:
				chan = msg[3][1:]
				self.sock.join(chan)
			print("* [IRC] Invited to {0}, by {1}. Attempting to join.".format(chan, person))	
		except:
			pass

	def Kicked(self, msg):
		if msg[3] == self.nickname:
			print("* [IRC] Kicked from {0} by {1} ({2}). Attempting to Auto-Rejoin.".format(msg[2], msg[0].split("!")[0], " ".join(msg[4:])[1:]))
			self.sock.join(msg[2])
		else:
			print("* [IRC] {0} was kicked from {1} by {2}; Reason ({3})".format(msg[3], msg[2], msg[0].split("!")[0], " ".join(msg[4:])[1:]))
	
	def Joined(self, msg):
		'''Someone joined, add them to allowed, with level 5 access, no hostname, and add them to the channel users list.'''
		person, host = msg[0].split("!")
		chan = msg[2].strip(":")
		print("* [IRC] {0} ({1}) joined {2}.".format(person, host, chan))		
		try:
			if person not in self.allowed.keys:
				self.allowed.db[person] = [None, 5]
			self.Users.Userlist[chan].append(person)
		except:
			pass
		
		
	def Parted(self, msg):
		'''Someone parted a channel, remove them from the channel users list.'''
		person, host = msg[0].split("!")
		print("* [IRC] {0} ({1}) parted {2}.".format(person, host, msg[2]))
		try:
			self.Users.Userlist[msg[2]].remove(person)
		except:
			pass
		
	def Quitted(self, msg):
		person, host = msg[0].split("!")
		print("* [IRC] {0} ({1}) has quit.".format(person, host))
		try:
			for chan in self.Users.Userlist.keys():
				if person in self.Users.Userlist[chan]:
					self.Users.Userlist[chan].remove(person)
		except:
			pass
			
	def Nickchange(self, msg):
		person, host = msg[0].split("!")
		new = msg[2][1:]
		print("* [IRC] {0} has changed nick to {1}.".format(person, new))
		try:
			for chan in self.Users.Userlist.keys():
				if person in self.Users.Userlist[chan]:
					self.Users.Userlist[chan].remove(person)
					self.Users.Userlist[chan].append(new)
			if new not in self.allowed.keys:
				self.allowed.db[new] = [None, 5]
		except:
			pass
			
	def Modechange(self, msg):
		person, host = msg[0].split("!")
		if len(msg[3]) > 2: #Multiple modes set
			print("* [IRC] {0} ({1}) set modes {2} on channel {3}.".format(person, host, " ".join(msg[3:]), msg[2]))
		else:
			print("* [IRC] {0} ({1}) set mode {2} on channel {3}.".format(person, host, " ".join(msg[3:]), msg[2]))
		
	def CTCP(self, ctcp, location, message):
		'''CTCP'd. Lets respond.'''
		self.sock.send("NOTICE {0} :{1}".format(location, message))
		print("* [CTCP {0} from {1}] Replying with: '{2}'".format(ctcp, location, message))

	def NoTopic(self, msg):
		print("* [IRC] There is no topic set for {0}".format(msg[3]))

	def Topic(self, msg):
		print("* [IRC] Topic for {0} set to {1}".format(msg[3] , " ".join(msg[4:])[1:]))

	def TopicTime(self, msg):
		print(datetime.fromtimestamp(int(msg[5])).strftime("* [IRC] Topic for {0} set by {1} at %c".format(msg[3], msg[4])))

	def Who(self, msg):
		person, host = msg[7], msg[4]+"@"+msg[5]
		print("* [IRC] {0} has Ident/Host of '{1}' and Realname of '{2}'.".format(person, host, " ".join(msg[10:])))
		if "*" in msg[8]:
			print("* [IRC] {0} is an IRC Operator on {1}.".format(person, msg[6]))
		if 'H' in msg[8]:
			print("* [IRC] {0} is currently available.".format(person))
		if 'G' in msg[8]:
			print("* [IRC] {0} is currently away.".format(person))
		
	def Names(self, msg):
		nameslist = []
		for x in msg[5:]:
			x = x.replace(":","").replace("~","").replace("&","").replace("@","").replace("%","").replace("+","")
			nameslist.append(x)
			if x not in self.allowed.db.keys():
				self.allowed.db[x] = [None, 5]
		self.Users.Userlist[msg[4]] = nameslist	
		print("* [IRC] Users on {0}: {1}".format(msg[4], " ".join(nameslist)))

	def MOTD(self, msg):
		print("* [MOTD] {0}".format(" ".join(msg[3:])))

	def Banned(self, msg):
		print("* [IRC] Cannot join {0}, Banned (+b).".format(msg[3]))

	def BannedVoice(self, msg):
		print("* [IRC] Cannot speak in {0}; Banned/No voice.".format(msg[3]))

	def Welcome(self, msg):
		print("* [IRC] {0}, {1}".format(" ".join(msg[3:-1])[1:], msg[2]))

	def _Welcome(self, msg):
		print("* [IRC] {0}".format(" ".join(msg[3:])[1:]))

	def UserCount(self, msg):
		print("* [IRC] {0}".format(" ".join(msg[3:])[1:]))

	def IgnoreLine(self, msg):
		pass
