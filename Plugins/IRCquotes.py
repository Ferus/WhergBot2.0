#!/usr/bin/python2
import linecache
import random

class quotes():	
	def quotenum(self, number):
		self.number = number
		if self.number[0] == "-":
			return "You cannot have a negative quote."
		else:
			linecache.checkcache("quotes.txt")
			with open("quotes.txt") as q:
				for n, line in enumerate(q):
					pass
				self.linecount = n + 1
				if int(self.number) > self.linecount or self.number < 0:
					return "That quote number does not exist."
				else:
					self.quote = linecache.getline("quotes.txt", int(number)).strip('\n')
					return self.quote
				
	def count(self):
		linecache.checkcache("quotes.txt")
		with open("quotes.txt") as q:
			for n, line in enumerate(q):
				pass
			self.linecount = n + 1
			return "Quote count is at {0}".format(self.linecount)
	
	def random(self):
		linecache.checkcache("quotes.txt")
		with open("quotes.txt") as q:
			for n, line in enumerate(q):
				pass
			self.linecount = n + 1
			self.randomquote = random.randint(1, self.linecount)
			self.randomquote = linecache.getline("quotes.txt", int(self.randomquote)).strip('\n')
			return self.randomquote
			
	def add(self, text):
		self.text = text
		self.quotes = open('quotes.txt','a')
		if self.text != '':
			self.quotes.write("{0}".format(self.text+"\n"))
			self.quotes.close()
			return "A new quote has been added!"
		else:
			return "You attempted to add a quote with no length."
	
	def find(self, text):
		master_list = {}
		self.text = text
		self.quotes = open('quotes.txt','r')
		if self.text != '':
			for i, line in enumerate(self.quotes):
				if text in line:
					master_list[i+1] = line.strip("\n")
			keys = str(master_list.keys()).strip("[").strip("]")
			if len(master_list.keys()) > 1:
				key_list = master_list.keys()
				key_list.sort()
				key_list = str(key_list).strip("[").strip("]")
				return "Found {0} quotes with the search term '{1}'. Quotes {2}.".format(len(master_list.keys()), text, key_list)
			elif len(master_list.keys()) == 0:
				return "Found 0 quotes with the search term '{0}'.".format(text)
			else:
				return "Found 1 quote with the search term '{0}'. Quote {1}".format(text, keys)
		else:
			return "You must give a search term to use this command."
		self.quotes.close()
