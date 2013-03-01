#!/usr/bin/env python

import sqlite3
import time

class Seen(object):
	def __init__(self, database=":memory:"):
		self.database = database
		self.Conn = sqlite3.connect(self.database, check_same_thread = False)
		self.Cursor = self.Conn.cursor()
		self.Cursor.execute("CREATE TABLE IF NOT EXISTS lastseen (nick TEXT PRIMARY KEY, channel TEXT, last_msg TEXT, timestamp DATE)")

	def getLastSeen(self, nick):
		results = self.Cursor.execute("SELECT channel, last_msg, timestamp FROM lastseen WHERE nick=?", [nick])
		try:
			channel, last_msg, timestamp = results.fetchone()
			return (nick, channel, last_msg, timestamp)
		except TypeError:
			return None

	def addLastSeen(self, nick, channel, last_msg):
		timestamp = time.time()
		x = self.Cursor.execute("SELECT COUNT(0) FROM lastseen WHERE nick=?", [nick])
		if x.fetchone()[0] == 0:
			self.Cursor.execute("INSERT INTO lastseen VALUES (?, ?, ?, ?)", [nick, channel, last_msg, timestamp])
		else:
			self.Cursor.execute("UPDATE lastseen SET channel=?, last_msg=?, timestamp=? WHERE nick=?", [channel, last_msg, timestamp, nick])
		self.Conn.commit()



