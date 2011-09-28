#!/usr/bin/python2
#Global Imports
from threading import Thread
from datetime import datetime
import time

#Local Imports
import Commands

class Parse():
	def __init__(self, sock=None, allowed=None, nick=None):
		self.sock = sock
		self.allowed = allowed	
		self.nickname = nick
		
		self.users = {} #Storage for Users of each channel. The Key is channel, users are a list.
		
		self.command = Commands.Commands(sock=self.sock, parser=self, nick=self.nickname, allowed=self.allowed)
		self._commands = self.command.cmds.keys()
		
		self.cmdVar = '$'
		self.ctcpReplies = {"\x01VERSION\x01" : "I am WhergBot, A Python based IRC bot.",
							"\x01TIME\x01" : "The local time here is {0}",
							"\x01SOURCE\x01" : "My latest source can be found at https://github.com/Ferus/WhergBot",
							}
							
		
	def Main(self, msg):
		'''Main Parser, Here we take raw data, and split at \r\n.'''
		tmp = msg.splitlines()

		if len(tmp) >1: #Somehow this handles the bunched up lists when connecting. Weird.
			for msg in tmp:
				msg = msg.split()
				#print(msg) #Temporary printing here, until we define the rest of the parser.
				
				try:
					if msg[1] == '331':
						print("* [IRC] There is no topic set for {0}".format(msg[3]))
					if msg[1] == '332':
						print("* [IRC] Topic for {0} set to {1}".format(msg[3] , " ".join(msg[4:])[1:]))
				
					if msg[1] == '333':
						print(datetime.fromtimestamp(int(msg[5])).strftime("* [IRC] Topic for {0} set by {1} at %c".format(msg[3], msg[4])))
					
					if msg[1] == '352':						
						'''<channel> <user> <host> <server> <nick> <H|G>[*][@|+] :<hopcount> <real name>
						[':opsimathia.datnode.net', '352', 'WhergBot2', '#hacking', 'anonymous', 'the.interwebs', 'opsimathia.datnode.net', 'Ferus', 'Hr*', ':0', 'Matt']'''
						person, host = msg[7], msg[4]+"@"+msg[5]
						
						print("* [IRC] {0} has Ident/Host of '{1}' and Realname of '{2}'.".format(person, host, " ".join(msg[10:])))
						
						if "*" in msg[8]:
							print("* [IRC] {0} is an IRC Operator on {1}.".format(person, msg[6]))
						if 'H' in msg[8]:
							print("* [IRC] {0} is currently available.".format(person))
						if 'G' in msg[8]:
							print("* [IRC] {0} is currently away.".format(person))
							
					if msg[7] == 'KILL':
						print("* [IRC] {0} killed by oper {1}. Reason: {2}".format(msg[10], msg[12], " ".join(msg[15:])))
					
					if msg[1] == 'QUIT':
						'''This was probably from a kill.'''
						self.Quitted(msg)							
						
					
					if msg[1] == '353':
						nameslist = []
						for x in msg[5:]:
							x = x.replace(":","").replace("~","").replace("&","").replace("@","").replace("%","").replace("+","")
							nameslist.append(x)
							
							if x not in self.allowed.db.keys():
								self.allowed.db[x] = [None, 5]
							
						self.users[msg[4]] = nameslist	
						print("* [IRC] Users on {0}: {1}".format(msg[4], " ".join(nameslist)))
						
				except:
					pass
					
		else:
			for msg in tmp:
				tmp = msg #The full message as a string.
				msg = msg.split() #The message split, a list of strings.
				#print(msg) #Temporary printing here, until we define the rest of the parser.

				try:
					# Parts, Joins, Kicks, All IRC actions
					if msg[1] == 'KICK' and msg[3] == self.nickname:
						'''Auto-rejoin if we are kicked.'''
						self.sock.send("JOIN {0}".format(msg[2]))
						print("* [IRC] Kicked from {0} by {1} ({2}). Autorejoining.".format(msg[2], msg[0].split("!")[0][1:], " ".join(msg[4:])[1:]))
						
					if msg[1] == 'PRIVMSG':
						self.Privmsg(tmp)
				
					if msg[1] == 'NOTICE':
						self.Notice(tmp)
						
					if msg[1] == 'INVITE':
						self.Invited(msg)			

					if msg[1] == 'JOIN':
						self.Joined(msg)
						
					if msg[1] == 'PART':
						self.Parted(msg)
						
					if msg[1] == 'QUIT':
						self.Quitted(msg)
						
					if msg[1] == 'NICK':
						self.Nickchange(msg)
						
					if msg[1] == 'MODE':
						self.Modechange(msg)
					
					else:
						pass #Havent finished defining everything.
	
				except:
					pass
					
	
	def Privmsg(self, msg):
		'''Parse for commands. Etc.'''
		try:
			Nick = self.Nick(msg)
			Host = self.Host(msg)
			Action = self.Action(msg)
			Location = self.Loc(msg)
			Text = self.Text(msg)
			Cmd = self.Cmd(msg)
			Msg = [Nick, Host, Action, Location, Text, Cmd]
			
			if Nick == Location:
				'''self.Loc() already handles where PM's come from, but now we need to change how it shows.'''
				Location = self.nickname
			
			'''If a command is called, check the hostname and access level of the person who called it, and if they have access, execute the command.'''
								
			if Cmd.startswith(self.cmdVar) and Cmd[1:] in self._commands:
				check = self.allowed.levelCheck(Nick)[1]
				if check[1] <= self.command.cmds[Cmd[1:]][1]:
					if self.command.cmds[Cmd[1:]][2]:
						if Host == check[0]:
							t = Thread(target=(self.command.cmds[Cmd[1:]])[0](Msg))
							t.daemon = True
							t.start()
						else:
							self.SendNotice(Nick, "You do not have the required authority to use this command.")
					else:
						t = Thread(target=(self.command.cmds[Cmd[1:]])[0](Msg))
						t.daemon = True
						t.start()
						
			if Text.startswith("\x01"):
				if Cmd in self.ctcpReplies.keys():
					'''The message received was a CTCP'''
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
						
			else:
				print("* [Privmsg] [{0}] <{1}> {2}".format(Location, Nick, Text))															
					
			if Cmd == 'DCC':
				'''I probably won't add dcc support.'''
				print("* [DCC] {0} request from {1}. Since DCC isnt implemented yet, we are just going to ignore this.".format(Text.split()[1], Nick))
				

				
		except Exception, e:
			print("* [Privmsg] Error")
			print(str(e))
			
	def Notice(self, msg):
		Nick = self.Nick(msg)
		Host = self.Host(msg)
		Action = self.Action(msg)
		Location = self.Loc(msg)
		Text = self.Text(msg)
		print("* [Notice] <{0}> {1}".format(Nick, Text))
	
	
	def Nick(self, msg):
		'''Parses the nick of a person who sent a message'''
		try:
			n = msg.split("!")[0].strip(":")
			return n
		except:
			return ''
			
	def Host(self, msg):
		'''Parses the Ident@Host of a person who sent a message'''
		try:
			h = msg.split("!")[1].split(" ")[0]
			return h
		except:
			return ''
		
	def Text(self, msg):
		'''Parses out the text in a message'''
		try:
			t = msg.split(" :")[1]
			return t
		except:
			return ''
		
	def Cmd(self, msg):
		'''Parses for a `command`'''
		try:
			c = msg.split(" :")[1].split()[0]	
			return c
		except:
			return ''
	
	def Loc(self, msg):
		'''Parses for the location from a PRIVMSG or NOTICE. If we are PM'd it returns the Nick of the person who PM'd us.'''
		try:
			l = msg.split()
			if l[2] == self.nickname:
				l = l[0].split("!")[0][1:]
			else:
				l = l[2]
			return l
		except:
			return ''
	
	def Action(self, msg):
		'''Parses for the type of action that is happening, IE: PRIVMSG, NOTICE'''
		try:
			a = msg.split()[1]
			return a
		except:
			return ''



	def Invited(self, msg):
		'''Join a channel we were invited to if the person's hostname is defined in allowed.'''
		try:
			person, host = msg[0].split(":")[1].split("!")
			if self.allowed.db[person][0] == host:
				chan = msg[3][1:]
				self.sock.join(chan)
			print("* [IRC] Invited to {0}, by {1}. Now joining.".format(chan, person))	
		except:
			pass

	def Joined(self, msg):
		'''Someone joined, add them to allowed, with level 5 access, no hostname, and add them to the channel users list.'''
		try:
			person, host = msg[0].split(":")[1].split("!")
			chan = msg[2].strip(":")
			if person not in self.allowed.keys:
				self.allowed.db[person] = [None, 5]
			self.users[chan].append(person)
			print("* [IRC] {0} ({1}) joined {2}.".format(person, host, chan))
		except:
			pass
		
		
	def Parted(self, msg):
		'''Someone parted a channel, remove them from the channel users list.'''
		try:
			person, host = msg[0].split(":")[1].split("!")
			self.users[msg[2]].remove(person)
			print("* [IRC] {0} ({1}) parted {2}.".format(person, host, msg[2]))
		except:
			pass
		
	def Quitted(self, msg):
		try:
			person, host = msg[0].split(":")[1].split("!")
			for chan in self.users.keys():
				if person in self.users[chan]:
					self.users[chan].remove(person)
			print("* [IRC] {0} ({1}) has quit.".format(person, host))
		except:
			pass
			
	def Nickchange(self, msg):
		try:
			person, host = msg[0].split(":")[1].split("!")
			new = msg[2][1:]
			for chan in self.users.keys():
				if person in self.users[chan]:
					self.users[chan].remove(person)
					self.users[chan].append(new)
			if person not in self.allowed.keys:
				self.allowed.db[person] = [None, 5]
			print("* [IRC] {0} has changed nick to {1}.".format(person, new))
		except:
			pass
			
	def Modechange(self, msg):
		try:
			person, host = msg[0].split(":")[1].split("!")
			if len(msg[3]) > 2: #Multiple modes set
				print("* [IRC] {0} ({1}) set modes {2} on channel {3}.".format(person, host, " ".join(msg[3:]), msg[2]))
			else:
				print("* [IRC] {0} ({1}) set mode {2} on channel {3}.".format(person, host, " ".join(msg[3:]), msg[2]))
		except:
			pass

		
	def CTCP(self, ctcp, location, message):
		'''CTCP'd. Lets respond.'''
		self.sock.send("NOTICE {0} :{1}".format(location, message))
		print("* [CTCP {0} from {1}] Replying with: '{2}'".format(ctcp, location, message))
						
	def SendRaw(self, msg):
		self.sock.send(msg)

	def SendMsg(self, location, msg):
		self.sock.say(location, msg)
	
	def SendNotice(self, location, msg):
		self.SendRaw("NOTICE {0} :{1}".format(location, msg))
		
		
