#!/usr/bin/env python

import os
from ConfigParser import ConfigParser

_CONFIGDEFAULTS = {
	"nick" : "WhergBot"
	,"real" : "Wherg"
	,"ident" : "Wherg"
	,"ownernick" : "Ferus"
	,"ownerhost" : "anonymous@the.interwebs"
	,"owneraccess" : "0"
	,"usessl" : "False"
	,"logging" : "False"
	,"server" : "opsimathia.datnode.net"
	,"port" : "6667"
	,"sslport" : "6697"
	,"channels" : "#hacking"
	,}

def LoadConfig(Profile='WhergBot'):
	"""Load the config file (If we can access it)
	If we can't, we make one."""
	if os.access("./Config.ini", 6):
		Config = ConfigParser(defaults=_CONFIGDEFAULTS)
		Config.read("./Config.ini")
		print("* [Config] Config file found. Loading config.")
		if not Config.has_section(Profile):
			import sys
			sys.exit("* [Config] No profile found with the name '{0}'. Please re-run WhergBot with the -r flag to make it.".format(Profile))
		return Config
	else:
		print("* [Config] No Config.ini file found. Would you like to create one now?")
		if raw_input("[Y/N] >> ").lower() not in ('y', 'yes'):
			import sys
			sys.exit("* [Config] You have chosen not to create a config file now. Run WhergBot.py with the -n flag to regenerate a config.")
		else:
			return MakeConfig()

def MakeConfig():
	"""Makes a new config.ini / Profile"""
	print("* [Config] You have chosen to (re-)create the config file.")
	Prof = ConfigParser(defaults=_CONFIGDEFAULTS)
	Prof.add_section('WhergBot')
	Prof = SetConfig(Prof, 'WhergBot')

	with open("./Config.ini", 'wb') as C:
		Prof.write(C)
	print("* [Config] Wrote config file to Config.ini.")
	return Prof

def NewProfile():
	Prof = ConfigParser(defaults=_CONFIGDEFAULTS)
	Prof.read("./Config.ini")
	print("* [Config] First off, what would you like to name the new profile?")

	NewConfig = GetAnswer(Prompt="New profile name >> ", isStr=True)
	print("* [Config] You have chosen to name the profile '{0}'.".format(NewConfig))

	Prof.add_section(NewConfig)
	Prof = SetConfig(Prof, NewConfig)

	with open("./Config.ini", 'wb') as C:
		Prof.write(C)

	print("* [Config] New profile has been written, Be sure to specify it when running with `WhergBot.py -p {0}`".format(NewConfig))
	return NewConfig

def SetConfig(Prof=None, ProfileName=''):
	"""Ask the user for profile options"""
	print("* [Config] What will the bots' nickname be?")
	Prof.set(ProfileName, 'Nick', GetAnswer(Prompt="Enter Bots' Name >> "))

	print("* [Config] What will the bots' realname be?")
	Prof.set(ProfileName, 'Real', GetAnswer(Prompt="Enter Bots' Realname >> "))

	print("* [Config] What will the bots' ident be?")
	Prof.set(ProfileName, 'Ident', GetAnswer(Prompt="Enter Bots' Ident >> "))

	print("* [Config] What channels will the bot join on start? (Separate with a comma)")
	Prof.set(ProfileName, 'Channels', GetAnswer(Prompt="Enter Channels (IE: `#lobby,#bots`) >> "))

	print("* [Config] What is the name of the bots' Owner? (Likely your nick.)")
	Prof.set(ProfileName, 'OwnerNick', GetAnswer(Prompt="Enter Owners IRC Nick >> "))

	print("* [Config] What is the hostmask of the bots' Owner? (Likely your hostmask.)")
	Prof.set(ProfileName, 'OwnerHost', GetAnswer(Prompt="Enter Owners Hostmask >> "))

	print("* [Config] What is the default access level of the owner? (If unsure, enter 0)")
	Prof.set(ProfileName, 'OwnerAccess', GetAnswer(Prompt="Enter Owners Access Level >> "))

	print("* [Config] What server will we be connecting to on start?")
	Prof.set(ProfileName, 'Server', GetAnswer(Prompt="Enter Server Address >> "))

	print("* [Config] Will we be using SSL to connect? (If unsure, enter 'False')")
	Prof.set(ProfileName, 'UseSSL', GetAnswer(Prompt="Enter SSL choice (True/False) >> ", isBool=True))

	print("* [Config] What port will be used with SSL? (Default 6697)")
	Prof.set(ProfileName, 'SSLPort', GetAnswer(Prompt="Enter default SSL port >> ", isInt=True))

	print("* [Config] What port will be used without SSL? (Default 6667)")
	Prof.set(ProfileName, 'Port', GetAnswer(Prompt="Enter default Non-SSL port >> ", isInt=True))

	print("* [Config] Will we be logging connections? (Default False)")
	Prof.set(ProfileName, 'Logging', GetAnswer(Prompt="Enter choice for logging (True/False) >> ", isBool=True))
	return Prof


def GetAnswer(Prompt=">> ", isInt=False, isBool=False):
	"""DrunkCode.py"""
	try:
		x = raw_input(Prompt)
		if not x or len(x) == 0:
			print("* [Config] You cannot pass a blank argument.")
			return GetAnswer()

		if isInt:
			if not x.isdigit():
				print("* [Config] This setting takes an int type. You entered '{0}' which is not an int.".format(x))
				return GetAnswer(isInt=True)
			else: x = int(x)

		if isBool:
			if x.lower() in ('true', 't'):
				return 'True'
			elif x.lower() in ('false', 'f'):
				return 'False'
			else:
				print("* [Config] This setting takes a bool type. You entered '{0}' which is not a bool.".format(x, type(x)))
				return GetAnswer(isBool=True)
		return x
	except EOFError:
		print("\n* [Config] That input was not valid.")
		return GetAnswer(isInt=isInt, isBool=isBool)


if __name__ == '__main__':
	import sys
	if not sys.stdout.isatty():
		sys.exit("Not a terminal bud. Don't have a GUI made yet. ;)")
	from optparse import OptionParser
	parser = OptionParser()
	parser.add_option("-n", "--new-config", dest="Newfile", action="store_true", default=False, help="Generate a new config file")
	parser.add_option("-r", "--new-profile", dest="Newprof", action="store_true", default=False, help="Add a new profile to the config")
	parser.add_option("-p", "--profile", dest="Profile", help="Specify a profile")
	(options, args) = parser.parse_args()
	
	# im sure this is broken.
	if options.Newfile and options.Profile or \
		options.Newfile and options.Newprof or \
			options.Profile and options.Newprof:
		sys.exit("You cannot specify multiple flags.")

	if options.Profile:
		Profile = options.Profile

	if options.Newprof:
		Profile = NewProfile()

	if options.Newfile:
		if os.access("./Config.ini", 6):
			if raw_input("* [Config] Would you like to backup the old config file?\n[Y/N] >> ").lower() in ("y","yes"):
				os.rename("./Config.ini", "./Config.ini.bak")
				print("* [Config] Backed up the old config file.")
			else:
				os.remove("./Config.ini")
				print("* [Config] We will not backup the old config file.")
		Profile = 'WhergBot'

	Config = LoadConfig(Profile)
	print("* [Config] Using profile '{0}'.".format(Profile))

	for key in _CONFIGDEFAULTS.keys():
		if not Config.has_option(Profile, key):
			sys.exit("* [Config] Missing option in config file, '{0}'.".format(key))

	import Core
	from threading import Timer
	WhergBot = Core.Bot(
		nickname = Config.get(Profile, "nick"),
		realname = Config.get(Profile, "real"),
		ident = Config.get(Profile, "ident"),
		owner = [Config.get(Profile, "ownernick"), Config.get(Profile, "ownerhost"), Config.getint(Profile, "owneraccess")],
		ssl = Config.getboolean(Profile, "usessl"),
		proxy = None,
		logging = Config.getboolean(Profile, "logging"))

	try:
		if Config.getboolean(Profile, 'usessl'):
			port = Config.getint(Profile, 'port')
		else:
			port = Config.getint(Profile, 'sslport')

		#port = Config.getint(Profile, 'port') if not Config.getboolean(Profile, 'usessl') else Config.getint(Profile, 'sslport')
		WhergBot.Connect(server=Config.get(Profile, "server"), port=port)
		if WhergBot.Nickserv.password != '':
			_n = Timer(3, WhergBot.Nickserv.Identify, ())
			_n.daemon = True
			_n.start()
		_t = Timer(5, WhergBot.irc.join, (Config.get(Profile, "Channels"),))
		_t.daemon = True
		_t.start()

		while WhergBot.irc._isConnected:
			Msg = WhergBot.irc.recv()
			WhergBot.Parse(Msg)

	except KeyboardInterrupt:
		print("\n* [Core] Interrupt Caught; Quitting!")
		WhergBot.p.command.Quit("KeyboardInterrupt Caught!")
