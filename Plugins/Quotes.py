#!/usr/bin/python2
from random import choice
import cPickle as pickle
import os, re

class IRCQuotes(object):
	def __init__(self, QuoteFile=None):
		'''IRCQuotes class, takes the QuoteFile arg of a filename to load. The file must be pickled.'''
		if QuoteFile:
			try:
				self.QuoteFile = QuoteFile
				
				try:
					_QuoteF = open(self.QuoteFile, "rb")
				except:
					pass
					#The file cant be opened, does it exist? if not, make it.
					#We have to dump an empty list to the file and pickle it
				else:
					with _QuoteF:
						self.QuoteP = pickle.load(_QuoteF)
						
					
				self.QuoteCount = len(self.QuoteP)
				print("* [Quotes] Loading Quote File: {0}".format(str(self.QuoteFile)))
				
			except Exception, e:
				print("* [Quotes] Error: {0}".format(repr(e)))
		else:
			print("* [Quotes] Error: No Quote File specified.")
			
	def Save(self):
		try:
			pickle.dump(self.QuoteP, open(self.QuoteFile, 'wb'))
			print("* [Quotes] Successful pickle dump to {0}".format(self.QuoteFile))			
		except:
			print("* [Quotes] Error: Problem saving quotes.")
			
	def Add(self, QuoteString=''):
		if QuoteString != '':
			try:
				self.QuoteCount += 1
				self.QuoteP.append(QuoteString)
				print("* [Quotes] Added new quote.")
				self.Save()
				return "Added new quote number '{0}' successfully.".format(self.QuoteCount)
			except:
				print("* [Quotes] Error: Could not add quote.")
				return "Error adding quote to quote database."
		else:
			print("* [Quotes] No string to add to quotes.")
			return "I cannot add a null string to my quotes database."
	
	def Del(self, QuoteNum=None):
		try:
			if type(QuoteNum) == int:
				del self.QuoteP[QuoteNum-1]
				self.QuoteCount -= 1
				self.Save()
				return "Removed quote number {0} from my database.".format(QuoteNum)
			else:
				return "{0} is not a valid quote number.".format(QuoteNum)
		except Exception, e:
			print("{0}".format( repr(e) ))
		
	def Number(self, QuoteNum=None):
		try:
			if QuoteNum != None:
				if QuoteNum.isdigit():
					'''Test if we are passed a number.'''
					QuoteNum = int(QuoteNum)
					if QuoteNum > 0 and QuoteNum <= self.QuoteCount:
						QuoteNum -= 1 #The DB starts at 0. We have to convert what the humans think.
						print("* [Quotes] Sending IRC Quote")
						return self.QuoteP[QuoteNum]
					else:
						return "I'm sorry, but I don't have that quote in my database."
				else:
					print("* [Quotes] Sending random Quote.")
					return choice(self.QuoteP)
			else:
				print("* [Quotes] Sending random Quote.")
				return choice(self.QuoteP)			
		except:
			pass
			
	def Count(self):
		return "I currently hold {0} quotes in my database.".format(self.QuoteCount)
		
	def Search(self, msg=''):
		if msg == '':
			return "I cannot search for a null string. Please supply a string to search for."
			
		_quotenums = []
		for num, quote in enumerate(self.QuoteP):
			if re.search(msg, quote):
				_quotenums.append(str(num+1))
				
		if len(_quotenums) == 1:
			return "I found 1 quote matching the string '{0}': Quote number {1}".format(msg, _quotenums[0])
			
		elif len(_quotenums) > 1:
			return "I found {0} quotes matching the string '{1}': Quote numbers {2}".format(len(_quotenums), msg, ", ".join(_quotenums))
				
		elif len(_quotenums) == 0:
			return "I did not find any quotes matching the string '{0}': Please redefine your search.".format(msg)
			
	def Backup(self, BackupFile=None):
		'''Backup the quotes file to a .txt just in case.'''
		if BackupFile == None:
			BackupFile = "IRCQuotes.txt"
		
		if os.access(BackupFile, 6): # Test if we have read and write access to the file, rather than assuming.
			try:
				os.unlink(BackupFile) #Remove the old one
				print("* [Quotes] Removing old quotes file.")
				with open(BackupFile, "wb") as _BFile:
					for _q in self.QuoteP:
						_BFile.write(_q+"\n")
				print("* [Quotes] Created backup quotes file at {0}".format(str(BackupFile)))
				return "Created backup file {0}".format(BackupFile)
			except Exception, e:
				return "Error: {0}".format(repr(e))
			
		else: # Either we have no access, or the file doesnt exist.
			if os.access(BackupFile, os.F_OK): #Test if it exists.
				print("* [Quotes] Backup file permission error. Please check '{0}' for read and write permissions.".format(str(BackupFile)))
				return "Backup file exists, but I cannot read it or write to it. Please check file permissions on '{0}'.".format(str(BackupFile))
			else: #It doesnt exist. Make it.
				open(BackupFile, "wb").close()
				self.Backup(BackupFile=BackupFile)
				

		
