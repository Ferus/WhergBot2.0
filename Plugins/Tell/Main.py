#!/usr/bin/env python

import sqlite3
from .Settings import Settings

class Main(object):
	def __init__(self, Name, Parser):
		self.__name__ = Name
		self.Parser = Parser
		self.IRC = self.Parser.IRC
		self.Connection = sqlite3.connect(Settings.get("database", ":memory:"), check_same_thread = False)
		cur = self.Connection.cursor()
		cur.execute('CREATE TABLE IF NOT EXISTS tell ('
			'id INTEGER PRIMARY KEY AUTOINCREMENT,'
			'name TEXT,'
			'message TEXT,'
			'origin TEXT)')
		del cur

	def addTell(self, name, message, origin):
		cur = self.Connection.cursor()
		try:
			cur.execute("INSERT INTO tell (name, message, origin) VALUES (?, ?, ?)", [name, message, origin])
			self.Connection.commit()
			return True
		except Exception as e:
			return False

	def getTell(self, name):
		cur = self.Connection.cursor()
		cur.execute("SELECT id, message, origin FROM tell WHERE name=?", [name])
		return cur.fetchall()

	def sendPerson(self, name):
		cur = self.Connection.cursor()
		cur.execute("SELECT COUNT(id), origin FROM tell WHERE name=? GROUP BY origin", [name])
		h = cur.fetchone()
		if not h:
			return None
		self.IRC.say(name, "You have \x02{0}\x02 new message{1} from \x02{2}\x02.".format(
			h[0], "" if h[0] == 1 else "s", h[1]))

		messages = self.getTell(name)
		for msg in messages:
			self.IRC.say(name, "{0}: {1}".format(msg[2], msg[1]))
			cur2 = self.Connection.cursor()
			cur2.execute("DELETE FROM tell WHERE id=?", [msg[0]])

	def getName(self, data):
		name = data[0].split("!")[0]
		self.sendPerson(name)

	def handleTell(self, data):
		origin = data[0].split("!")[0]
		name = data[4]
		msg = " ".join(data[5:])
		if self.addTell(name, msg, origin):
			self.IRC.say(origin, "Your message has been sent! {0} will see it the next time I see them.".format(name))


	def Load(self):
		self.Parser.hookCommand('PRIVMSG', self.__name__,
			{".*": self.getName
			,"^@tell \S+ .*$": self.handleTell
			})
		self.Parser.hookCommand('JOIN', self.__name__, {".*": self.getName})

	def Unload(self):
		self.Connection.commit()
	def Reload(self):
		pass
