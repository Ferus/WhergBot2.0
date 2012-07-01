#!/usr/bin/env python
from Plugins.Modules import Torrents
from CommandLock import Locker

tpbL = Locker(3)
class ThePirateBay(Torrents.ThePirateBaySearch):

	def Main(self, Message, Sock, Users, Allowed):
		if tpbL.Locked:
			Sock.say(Message[0], "This command is locked at the moment.")
			return None

		x = " ".join(Message[4].split()[1:])
		try:
			cat, terms = x.split("[")[1].split("]")
		except:
			cat = "all"
			terms = x

		y = self.Request(terms.strip(" "), cat)
		for p in range(3):
			q = "\x02[TPB]\x02 {0} - {1} [{2} Seeds/{3} Leeches] {4}".format(y[str(p)]['title'], \
				y[str(p)]['size'], y[str(p)]['seed'], y[str(p)]['leech'], \
				y[str(p)]['link'] if y[str(p)]['link'] else y[str(p)]['magnetlink'])

			Sock.say(Message[0], q)
		tpbL.Lock()

tpb = ThePirateBay()

hooks = {
	'^@tpb': [tpb.Main, 5, False],
	}

helpstring = ""
