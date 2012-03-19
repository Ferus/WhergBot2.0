#!/usr/bin/env python

# Creates a Quotes database for Quotes.py.
# Usage: ./CreateDB.py <path/to/flatfile.txt>
# Creates a database with the same name as the flatfile passed

# Currently only works for Quotes.

import sys, os
from Plugins.Quotes import QuotesDatabase

if __name__ == '__main__':
	try:
		flatfile = sys.argv[-1]
	except Exception, e:
		sys.exit(repr(e))
	
	dbfile = flatfile.split(os.sep)[-1].split('.')[0]+'.db'
	if raw_input("Create database {0}? Y/N: ".format(dbfile)).lower() not in ('y', 'yes'):
		sys.exit("Quitting.")
	QuoteDB = QuotesDatabase(dbfile)
	
	with open(flatfile, "r") as quotes:
		while True:
			q = quotes.readline().strip('\n')
			if q == "":
				break
			print("Adding quote \"{0}\"".format(q))
			QuoteDB.Add(q)
	print("Created Database!")
	sys.exit()

