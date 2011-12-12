#!/usr/bin/python2
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
			_Fish = [f for f in F.readlines()]
		self.Fish = []
		for f in _Fish:
			self.Fish.append(f.strip())

	def GetFish(self):
		return random.choice(self.Fish)

	def GetPerson(self, Channel, Users):
		return random.choice(Users.GetUserList(Channel))

	def Parse(self, Msg, Sock, Users, Allowed):
		tmp = Msg[4].split()[1:]
		if tmp[0] == 'random' and tmp[1] == 'random':
			#All random.
			Person = self.GetPerson(Msg[3], Users)
			Fish = self.GetFish()
			Sock.action(Msg[3], "slaps {0} around a bit with {1}.".format(Person, Fish))

		elif tmp[0] == 'random' and tmp[1] != 'random':
			#Random person
			Person = self.GetPerson(Msg[3], Users)
			Sock.action(Msg[3], "slaps {0} around a bit with {1}.".format(Person, " ".join(tmp[1:])))

		elif tmp[0] != 'random' and tmp[1] == 'random':
			#Random fish
			Fish = self.GetFish()
			Sock.action(Msg[3], "slaps {0} around a bit with {1}.".format(tmp[0], Fish))

		elif tmp[0] != 'random' and tmp[1] != 'random':
			#No random
			Sock.action(Msg[3], "slaps {0} around a bit with {1}.".format(tmp[0], " ".join(tmp[1:])))
		else:
			Sock.say(Msg[3], "Error'd.")

S = Slap("Plugins/Fish.txt")

hooks = {
	"^@slap" : [S.Parse, 5, False],
	}
