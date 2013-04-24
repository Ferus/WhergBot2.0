#!/usr/bin/env python

import sqlite3

class Seen(object):
	def __init__(self, database=":memory:"):
		self.database = database
		self.Conn = sqlite3.connect(self.database, check_same_thread = False)
		self.Cursor = self.Conn.cursor()
		self.Cursor.execute("""CREATE TABLE IF NOT EXISTS lastseen
			(nick TEXT PRIMARY KEY
			,channel TEXT
			,last_msg TEXT
			,timestamp DATE DEFAULT (strftime('%s', 'now'))
			)""")

	def getLastSeen(self, nick):
		results = self.Cursor.execute("SELECT channel, last_msg, timestamp FROM lastseen WHERE nick=?", [nick])
		try:
			channel, last_msg, timestamp = results.fetchone()
			return (nick, channel, last_msg, timestamp)
		except TypeError:
			return None

	def addLastSeen(self, nick, channel, last_msg):
		nick = nick.lower()
		x = self.Cursor.execute("SELECT COUNT(0) FROM lastseen WHERE nick=?", [nick])
		if x.fetchone()[0] == 0:
			self.Cursor.execute("INSERT INTO lastseen (nick, channel, last_msg) VALUES (?, ?, ?)", [nick, channel, last_msg])
		else:
			self.Cursor.execute("UPDATE lastseen SET channel=?, last_msg=?, timestamp=strftime('%s', 'now') WHERE nick=?", [channel, last_msg, nick])
		self.Conn.commit()



