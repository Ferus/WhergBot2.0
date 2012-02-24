#!/usr/bin/env python
import random

class Slap(object):
	def __init__(self, FishFile=None):
		'''
		The provided Fish.txt file was obtained from
		https://github.com/jamer/Rubot/blob/master/plugins/Slap.rb
		Some of these 'fish' only exist because of a huge slap
		battle between myself and an IRC friend.
		'''

		if not FishFile:
			FishFile = "Fish.txt"
		with open(FishFile, "r") as F:
			self.Fish = F.read().splitlines()

	def Parse(self, Msg, Sock, Users, Allowed):
		try:
			tmp = Msg[4].split()[1:]
			if tmp[0] == 'random' and tmp[1] == 'random':
				#All random.
				Person = random.choice(Users.GetUserList(Msg[3]))
				Sock.action(Msg[3], "slaps {0} around a bit with {1}.".format(Person, random.choice(self.Fish)))

			elif tmp[0] == 'random' and tmp[1] != 'random':
				#Random person
				Person = self.GetPerson(Msg[3], Users)
				Sock.action(Msg[3], "slaps {0} around a bit with {1}.".format(Person, " ".join(tmp[1:])))

			elif tmp[0] != 'random' and tmp[1] == 'random':
				#Random fish
				Sock.action(Msg[3], "slaps {0} around a bit with {1}.".format(tmp[0], random.choice(self.Fish)))

			elif tmp[0] != 'random' and tmp[1] != 'random':
				#No random
				Sock.action(Msg[3], "slaps {0} around a bit with {1}.".format(tmp[0], " ".join(tmp[1:])))

		except:
			Sock.notice(Msg[0], "@slap takes two arguments. The person and the object. Either can be 'random'")

S = Slap("Plugins/Fish.txt")

hooks = {
	"^@slap" : [S.Parse, 5, False],
	}

helpstring = """Slaps a person with either a random `fish` or an object.
@slap <person> <object>: Slaps a person with <object>
@slap <person> random: Slaps a person with a random `fish`
@slap random <object>: Slaps a random person with <object>
@slap random random: Slaps a random person with a random `fish`"""
