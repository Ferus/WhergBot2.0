#!/usr/bin/env python

import Core

import os
from threading import Timer
from ConfigParser import ConfigParser
cParser = ConfigParser

def LoadConfig(Profile='WhergBot'):
	if os.access("./Config.ini", os.R_OK):
		Config = cParser()
		Config.read("./Config.ini")
		print("* [Config] Config file found. Loading config.")
		if not Config.has_section(Profile):
			print(Config._sections)
			import sys
			sys.exit("* [Config] Config file is missing an important section. Please re-run WhergBot with the -r flag.")
		try:
			return Config
		except:
			import sys
			sys.exit("* [Config] Failed to load config. Please re-run WhergBot with the -r flag.")
	else:
		print("* [Config] No Config.ini file found. Would you like to create one now?")
		if raw_input("[Y/N] >> ").lower() not in ('y', 'yes'):
			import sys
			sys.exit("* [Config] You have chosen not to create a config file now. Run WhergBot.py with the -r flag to regenerate a config.")
		else:
			return MakeConfig()

def MakeConfig(AddNewProfile=False):
	# Shoulda made this one function and return a dict.
	if not AddNewProfile:
		print("* [Config] You have chosen to (re-)create the config file.")
		Prof = cParser()
		Prof.add_section('WhergBot')
		Prof = SetConfig(Prof, 'WhergBot')

		with open("./Config.ini", 'wb') as C:
			Prof.write(C)
		print("* [Config] Wrote config file to Config.ini.")
		return Prof

	else:
		Prof = cParser()
		Prof.read("./Config.ini")
		print("* [Config] First off, what would you like to name the new profile?")

		NewConfig = GetAnswer(Prompt="New profile name >> ", isStr=True)
		print("* [Config] You have chosen to name the profile '{0}'.".format(NewConfig))

		Prof.add_section(NewConfig)
		Prof = SetConfig(Prof, NewConfig)

		with open("./Config.ini", 'wb') as C:
			Prof.write(C)

		print("* [Config] New profile has been written, Be sure to specify it when running with `WhergBot.py -p {0}`".format(NewConfig))

		return Prof

def SetConfig(Prof=None, ProfileName=''):
		print("* [Config] What will the bots' nickname be?")
		Prof.set(ProfileName, 'Nick', GetAnswer(Prompt="Enter Bots' Name >> ", isStr=True))
		print("* [Config] What will the bots' realname be?")
		Prof.set(ProfileName, 'Real', GetAnswer(Prompt="Enter Bots' Realname >> ", isStr=True))
		print("* [Config] What will the bots' ident be?")
		Prof.set(ProfileName, 'Ident', GetAnswer(Prompt="Enter Bots' Ident >> ", isStr=True))
		print("* [Config] What channels will the bot join on start? (Separate with a comma)")
		Prof.set(ProfileName, 'Channels', GetAnswer(Prompt="Enter Channels (IE: `#lobby,#bots`) >> ", isStr=True))
		print("* [Config] What is the name of the bots' Owner? (Likely your nick.)")
		Prof.set(ProfileName, 'OwnerNick', GetAnswer(Prompt="Enter Owners IRC Nick >> ", isStr=True))
		print("* [Config] What is the hostmask of the bots' Owner? (Likely your hostmask.)")
		Prof.set(ProfileName, 'OwnerHost', GetAnswer(Prompt="Enter Owners Hostmask >> ", isStr=True))
		print("* [Config] What is the default access level of the owner? (If unsure, enter 0)")
		Prof.set(ProfileName, 'OwnerAccess', GetAnswer(Prompt="Enter Owners Access Level >> ", isInt=True))
		print("* [Config] What server will we be connecting to on start?")
		Prof.set(ProfileName, 'Server', GetAnswer(Prompt="Enter Server Address >> ", isStr=True))
		print("* [Config] Will we be using SSL to connect? (If unsure, enter 'False')")
		Prof.set(ProfileName, 'UseSSL', GetAnswer(Prompt="Enter SSL choice (True/False) >> ", isBool=True))
		print("* [Config] What port will be used with SSL? (Default 6697)")
		Prof.set(ProfileName, 'SSLPort', GetAnswer(Prompt="Enter default SSL port >> ", isInt=True))
		print("* [Config] What port will be used without SSL? (Default 6667)")
		Prof.set(ProfileName, 'Port', GetAnswer(Prompt="Enter default Non-SSL port >> ", isInt=True))
		print("* [Config] Will we be logging connections? (Default False)")
		Prof.set(ProfileName, 'Logging', GetAnswer(Prompt="Enter choice for logging (True/False) >> ", isBool=True))
		return Prof


def GetAnswer(Prompt=">> ", isStr=False, isInt=False, isBool=False):
	try:
		x = raw_input(Prompt)
		if not x or len(x) == 0:
			print("* [Config] You cannot pass a blank argument.")
			return GetAnswer()
		if isStr:
			if type(x) != str:
				print("* [Config] This setting takes a string type. You entered '{0}' which is a {1} type.".format(x, type(x)))
				return GetAnswer(isStr=True)
			else: pass

		if isInt:
			if not x.isdigit():
				print("* [Config] This setting takes an int type. You entered '{0}' which is a {1} type.".format(x, type(x)))
				return GetAnswer(isInt=True)
			else: x = int(x)

		if isBool:
			if x.lower() == 'true':
				return 'True'
			elif x.lower == 'false':
				return 'False'
			else:
				print("* [Config] This setting takes a bool type. You entered '{0}' which is not a bool.".format(x, type(x)))
				return GetAnswer(isBool=True)
		return x
	except EOFError:
		print("\n* [Config] That input was not valid.")
		return GetAnswer(isStr=isStr, isInt=isInt, isBool=isBool)


if __name__ == '__main__':
	import sys
	if not sys.stdout.isatty():
		sys.exit('Not a terminal bud.')
	from optparse import OptionParser
	parser = OptionParser()
	parser.add_option("-r", "--regenerate", dest="Newfile", action="store_true", default=False, help="Generate a new config file")
	parser.add_option("-p", "--profile", dest="Profile", help="Specify a profile")
	(options, args) = parser.parse_args()

	if options.Newfile and options.Profile:
		sys.exit("You cannot specify both flags.")

	if options.Profile:
		Profile = options.Profile

	if options.Newfile:
		if os.access("./Config.ini", 6):
			while True:
				if raw_input("* [Config] Would you like to backup the old config file?\n[Y/N] >> ").lower() in ("y","yes"):
					os.rename("./Config.ini", "./Config.ini.bak")
					print("* [Config] backed up the old config file.")
					break
				else:
					print("* [Config] We will not backup the old config file.")
		Profile = 'WhergBot'

	try:
		Config = LoadConfig(Profile)
		WhergBot = Core.Bot(
			nickname = Config.get(Profile, "nick"),
			realname = Config.get(Profile, "real"),
			ident = Config.get(Profile, "ident"),
			owner = [Config.get(Profile, "ownernick"), Config.get(Profile, "ownerhost"), Config.getint(Profile, "owneraccess")],
			ssl = Config.getboolean(Profile, "usessl"),
			proxy = None,
			logging = Config.getboolean(Profile, "logging"))

		WhergBot.Connect(server=Config.get(Profile, "server"), port=Config.getint(Profile, "sslport"))
		#	Config.getint(Profile, "port") - Non-SSL

		if WhergBot.Nickserv.password != '':
			_p = Timer(3, WhergBot.Identify, ())
			_p.daemon = True
			_p.start()
		_t = Timer(5, WhergBot.irc.join, (Config.get(Profile, "Channels"),))
		_t.daemon = True
		_t.start()

		while WhergBot.irc._isConnected:
			Msg = WhergBot.irc.recv()
			WhergBot.Parse(Msg)

	except KeyboardInterrupt:
		print("\n* [Core] Interrupt Caught; Quitting!")
		WhergBot.p.command.Quit("KeyboardInterrupt Caught!")
