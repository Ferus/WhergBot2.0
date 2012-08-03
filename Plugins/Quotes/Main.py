#!/usr/bin/env python
import os
import re
import sqlite3
from random import choice

from .Settings import Settings

class NoDatabaseError(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)
	def __unicode__(self):
		return repr(self.value.encode('utf8'))

class DefaultDatabase(object):
	def __init__(self, Database=None, Table=None, Row=None):
		if not Database:
			raise NoDatabaseError("Failed to pass a database name.")

		def regexp(expr, item):
			reg = re.compile(expr)
			return reg.search(item, re.IGNORECASE) is not None

		self.Table = Table

		self.Database = Database
		self.Conn = sqlite3.connect(self.Database, check_same_thread = False)
		self.Conn.create_function("REGEXP", 2, regexp)

		self.Cursor = self.Conn.cursor()
		self.Cursor.execute(
			"create table if not exists {0} (id integer primary key autoincrement, {1} TEXT)".format(self.Table, Row))

		try:
			self.LastID = str(self.Cursor.execute("SELECT * FROM {0} ORDER BY ID DESC LIMIT 1".format(self.Table)).next()[0])
		except StopIteration, e:
			self.LastID = "0"
		print("* [Quotes.py] {0} rows from {1} have been loaded.".format(self.LastID, self.Table))

	def Save(self):
		self.Conn.commit()
		print("* [Quotes.py] Saving Database!")

	def Add(self, String):
		try:
			x = self.Cursor.execute("insert into {0} values (NULL, ?)".format(self.Table), (String.decode("utf8"),))
			self.LastID = str(x.lastrowid)
			print("* [Quotes.py] Added new string to {0}!".format(self.Table))
			self.Save()
			return "Added new quote number {0} successfully!".format(self.LastID)
		except Exception, e:
			print("* [Quotes.py] Error 'adding'.\n* [Quotes.py] {0}".format(repr(e)))

class QuotesDatabase(DefaultDatabase):
	def Delete(self, QuoteNum):
		try:
			self.Cursor.execute("update quotes set quote='This quote has been deleted.' where id=?", (QuoteNum,))
			print("* [Quotes] Deleted quote number {0}".format(QuoteNum))
			self.Save()
			return "Deleted quote number {0} successfully".format(QuoteNum)
		except Exception, e:
			print("* [Quotes] Error 'deleting'.\n* [Quotes] {0}".format(repr(e)))

	def Number(self, QuoteNum):
		if type(QuoteNum) != int:
			return self.Random()
		try:
			x = self.Cursor.execute("select quote from quotes where id=?", (QuoteNum,))
			print("* [Quotes] Sending Quote.")
			return x.next()[0]

		except StopIteration, e:
			return "No quotes in database or quote does not exist."
		except Exception, e:
			return repr(e)

	def Random(self):
		print("* [Quotes] Sending random Quote.")
		y = choice(range(1, int(self.LastID)))
		x = self.Cursor.execute("select quote from quotes where id=?", (str(y),))
		return "Quote {0}: {1}".format(y, x.next()[0])

	def Count(self):
		return "I currently hold {0} quotes in my database.".format(self.LastID)

	def Search(self, msg=''):
		if msg == '':
			return "I cannot search for a null string. Please supply a string to search for."
		_quotenums = []

		for x in self.Cursor.execute('SELECT * FROM quotes WHERE quote REGEXP ?', (msg,)).fetchall():
			# x[0] == number. x[1] == quote.
			_quotenums.append(x[0])
		if len(_quotenums) >= 1:
			return "I found {0} quote{1} matching the string '{2}': Quote number{1} {3}".format(
				len(_quotenums),
				"s" if len(_quotenums) > 1 else "",
				msg,
				", ".join(str(y) for y in _quotenums))
		else:
			return "I didn't find any quotes matching the string '{0}': Please redefine your search.".format(msg)

	def Backup(self, BackupFile=None):
		'''Backup the quotes file to a .txt just in case.'''
		if BackupFile == None:
			BackupFile = "./Plugins/Quotes/IRCQuotes.txt"
		try:
			os.unlink(BackupFile) #Remove the old one
			print("* [Quotes] Removing old quotes file.")
			with open(BackupFile, "wb") as BFile:
				for q in self.Cursor.execute("select quote from quotes").fetchall():
					BFile.write(q[0].encode('utf8')+"\n")
			print("* [Quotes] Created backup quotes file at {0}".format(str(BackupFile)))
			return "Created backup file {0}".format(BackupFile)
		except Exception, e:
			return "Error: {0}".format(repr(e))

class RulesDatabase(DefaultDatabase):
	def Number(self, RuleNum):
		try:
			RuleNum = int(RuleNum)
		except:
			return "That's not a number!"
		try:
			x = self.Cursor.execute("select rule from rules where id=?", (RuleNum,))
			print("* [Rules] Sending Rule.")
			return x.next()[0]
		except StopIteration, e:
			return "No rules in database or rule does not exist."
		except Exception, e:
			return repr(e)

class Main(object):
	def __init__(self, Name, Parser):
		self.__name__ = Name
		self.Parser = Parser
		self.IRC = self.Parser.IRC

		self.Quotes = QuotesDatabase("./Plugins/Quotes/Quotes.db", "quotes", "quote")
		self.Rules = RulesDatabase("./Plugins/Quotes/Rules.db", "rules", "rule")

	def Quote(self, data):
		'''
		The main quote command. We check for any other data in the data sent.
		If its a number, we assume they are searching for a specific quote.
		'''
		try:
			Text = int(data[4])
		except:
			Text = None
		self.IRC.say(data[2], self.Quotes.Number(QuoteNum=Text))

	def QuoteSearch(self, data):
		'''Call the Search function of Quotes.py which uses re to find a quote'''
		if data[4:]:
			Text = " ".join(data[4:])
		else:
			Text = ''
		self.IRC.say(data[2], self.Quotes.Search(msg=Text))

	def QuoteCount(self, data):
		'''Returns the count of total quotes'''
		self.IRC.say(data[2], self.Quotes.Count())

	def QuoteAdd(self, data):
		'''Calls the add function to add a quote'''
		if not data[0] in Settings.get('allowed'): return None
		try:
			Text = " ".join(data[4:])
			self.IRC.say(data[2], self.Quotes.Add(String=Text))
		except:
			self.IRC.notice(data[0], "I cannot add a null string.")

	def QuoteDel(self, data):
		'''Calls the del function to remove a quote'''
		if not data[0] in Settings.get('allowed'): return None
		try:
			Text = int(data[4])
		except:
			Text = None
		self.IRC.say(data[2], self.Quotes.Delete(QuoteNum=Text))

	def QuoteBackup(self, data):
		'''Calls the backup function to backup the pickled quotes file in plaintext'''
		if not data[0] in Settings.get('allowed'): return None
		try:
			Text = data[4]
		except:
			Text = None
		self.IRC.say(data[2], self.Quotes.Backup(BackupFile=Text))

	def Rule(self, data):
		try:
			Text = int(data[4])
			self.IRC.say(data[2], self.Rules.Number(Text))
		except:
			self.IRC.notice(data[0].split('!')[0], "Supply a rule number!")

	def Load(self):
		self.Parser.hookCommand("PRIVMSG", "^@quote(?: \d{1,})?$", self.Quote)
		self.Parser.hookCommand("PRIVMSG", "^@qsearch .*?$", self.QuoteSearch)
		self.Parser.hookCommand("PRIVMSG", "^@qfind .*?$", self.QuoteSearch)
		self.Parser.hookCommand("PRIVMSG", "^@qcount$", self.QuoteCount)
		self.Parser.hookCommand("PRIVMSG", "^@qadd .*?$", self.QuoteAdd)
		self.Parser.hookCommand("PRIVMSG", "^@qdel \d{1,}$", self.QuoteDel)
		self.Parser.hookCommand("PRIVMSG", "^@qbackup(?: \W)?$", self.QuoteBackup)
		self.Parser.hookCommand("PRIVMSG", "^@rule \d{1,}$", self.Rule)

		self.Parser.hookPlugin(self.__name__, Settings, self.Load, self.Unload, self.Reload)

	def Unload(self):
		self.Quotes.Save()
		self.Rules.Save()
		del self.Quotes
		del self.Rules
		del self

	def Reload(self):
		pass
