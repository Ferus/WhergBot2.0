#!/usr/bin/env python
from random import choice
import os
import re
import sqlite3

class NoDatabaseError(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)

class DefaultDatabase(object):
	def __init__(self, Database=None, Table=None, Row=None):
		if not Database:
			raise NoDatabaseError("Failed to pass a database name.")

		def regexp(expr, item):
			reg = re.compile(expr)
			return reg.search(item, re.IGNORECASE) is not None
		
		self.Table = Table
		
		self.Database = Database
		self.Conn = sqlite3.connect(self.Database)
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
<<<<<<< HEAD
			self.Conn.commit()
			print("* [Quotes] Saving database!")
		except Exception, e:
			print("* [Quotes] OOPS! {0}".format(repr(e)))

	def Add(self, QuoteString):
		try:
			x = self.Cursor.execute("insert into quotes values (NULL, ?)", (QuoteString.decode("utf8"),))
=======
			x = self.Cursor.execute("insert into {0} values (NULL, ?)".format(self.Table), (String.decode("utf8"),))
>>>>>>> 52e4a0e0be6019ced5e235fed360a460d7fa843b
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
			BackupFile = "./Plugins/IRCQuotes.txt"
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

<<<<<<< HEAD
IRCq = QuotesDatabase("./Plugins/Quotes.db")
=======
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

IRCq = QuotesDatabase("./Plugins/Quotes.db", "quotes", "quote")
IRCr = RulesDatabase("./Plugins/Rules.db", "rules", "rule")
>>>>>>> 52e4a0e0be6019ced5e235fed360a460d7fa843b

def Quote(msg, sock, users, allowed):
	'''
	The main quote command. We check for any other data in the msg sent.
	If its a number, we assume they are searching for a specific quote.
	'''
	try:
		if msg[4].split()[1:]:
			Text = int(msg[4].split()[1:][0])
		else:
			Text = None
		sock.say(msg[3], IRCq.Number(QuoteNum=Text))
	except:
		pass

def QuoteSearch(msg, sock, users, allowed):
	'''Call the Search function of Quotes.py which uses re to find a quote'''
	if msg[4].split()[1:]:
		Text = " ".join(msg[4].split()[1:])
	else:
		Text = ''
	sock.say(msg[3], IRCq.Search(msg=Text))

def QuoteCount(msg, sock, users, allowed):
	'''Returns the count of total quotes'''
	sock.say(msg[3], IRCq.Count())

def QuoteAdd(msg, sock, users, allowed):
	'''Calls the add function to add a quote'''
	try:
		Text = " ".join(msg[4].split()[1:])
		sock.say(msg[3], IRCq.Add(QuoteString=q))
	except:
		sock.notice(msg[0], "I cannot add a null string.")

def QuoteDel(msg, sock, users, allowed):
	'''Calls the del function to remove a quote'''
	try:
		Text = msg[4].split()[1:][0]
	except:
		Text = None
	sock.say(msg[3], IRCq.Delete(QuoteNum=Text))

def QuoteBackup(msg, sock, users, allowed):
	'''Calls the backup function to backup the pickled quotes file in plaintext'''
	try:
		Text = msg[4].split()[1:][0]
	except:
		Text = None
	sock.say(msg[3], IRCq.Backup(BackupFile=Text))

<<<<<<< HEAD
=======
def Rule(msg, sock, users, allowed):
	try:
		Text = msg[4].split()[1:][0]
		sock.say(msg[3], IRCr.Number(Text))
	except:
		sock.notice(msg[0], "Supply a rule number!")
	
>>>>>>> 52e4a0e0be6019ced5e235fed360a460d7fa843b
hooks = {
	'^@quote': [Quote, 5, False],
	'^@qsearch': [QuoteSearch, 5, False],
	'^@qfind': [QuoteSearch, 5, False],
	'^@qcount': [QuoteCount, 5, False],
	'^@qadd': [QuoteAdd, 0, True],
	'^@qdel': [QuoteDel, 0, True],
	'^@qbackup': [QuoteBackup, 0, True],

	'^@rule': [Rule, 5, False],
	}

helpstring = """Stores IRC quotes/`rules` in a pickle file.
@quote <number>: Sends the specified quote, if no number is given, a random quote
@qsearch <regex>: Uses a regex to find quotes
@qfind <regex>: Same as @qsearch
@qcount: Sends the quote count
@qadd <quote>: adds a quote
@qdel <quotenumber>: deletes a quote
@qbackup <filename>: Creates a plaintext backup"""
