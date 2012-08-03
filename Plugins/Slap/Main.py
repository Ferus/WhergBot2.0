#!/usr/bin/env python
import random
from .Settings import Settings

class Main(object):
	def __init__(self, Name, Parser):
		'''
		The provided Fish.txt file was obtained from
		https://github.com/jamer/Rubot/blob/master/plugins/Slap.rb
		Some of these 'fish' only exist because of a huge slap
		battle between myself and an IRC friend.
		'''
		self.FishFile = Settings.get('FishFile', 'Plugins/Slap/Fish.txt')
		with open(self.FishFile, "r") as F:
			self.Fish = F.read().splitlines()

		self.__name__ = Name
		self.Parser = Parser
		self.IRC = self.Parser.IRC

	def Slap(self, data):
		try:
			tmp = data[4:]
			#if tmp[0] == 'random' and tmp[1] == 'random':
			#	#All random.
			#	Person = random.choice(Users.GetUserList(Msg[3]))
			#	self.IRC.action(data[2], "slaps {0} around a bit with {1}.".format(Person, random.choice(self.Fish)))

			#elif tmp[0] == 'random' and tmp[1] != 'random':
			#	#Random person
			#	Person = self.GetPerson(Msg[3], Users)
			#	self.IRC.action(data[2], "slaps {0} around a bit with {1}.".format(Person, " ".join(tmp[1:])))

			if tmp[0] != 'random' and tmp[1] == 'random':
				#Random fish
				self.IRC.action(data[2], "slaps {0} around a bit with {1}.".format(tmp[0], random.choice(self.Fish)))

			elif tmp[0] != 'random' and tmp[1] != 'random':
				#No random
				self.IRC.action(data[2], "slaps {0} around a bit with {1}.".format(tmp[0], " ".join(tmp[1:])))
		except:
			self.IRC.notice(data[0].split('!')[0], "@slap takes two arguments. The person and the object. Either can be 'random'")

	def Load(self):
		self.Parser.hookCommand('PRIVMSG', '^@slap( .*?)?$', self.Slap)
		self.Parser.hookPlugin(self.__name__, Settings, self.Load, self.Unload, self.Reload)

	def Unload(self):
		pass
	def Reload(self):
		pass
