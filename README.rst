A Python 2.7/3.x IRC bot based on the blackbox IRC module
=========================================================

Official IRC help channel can be found at http://webirc.datnode.net/ or irc.datnode.net (Port 6667) in #hacking

Dependencies
============
	Python 2.7.2 or 3.x

	blackbox IRC Macros `(Develop Branch) <https://github.com/proxypoke/blackbox_IRC-macros/>`_
	blackBox is a great module that's built over the IRC protocol. It's used here to manage connections to an IRC server.

Optional Dependencies
=====================
	`requests <https://github.com/kennethreitz/requests/>`_

	Requests is a very nice 'frontend' to urllib2 and is used widely across WhergBot plugins.

	`wordnik <https://github.com/wordnik/wordnik-python/>`_

	We use the wordnik API in ./Plugins/Dictionary.py

	`python-mpd <http://pypi.python.org/pypi/python-mpd/>`_

	For all you MPD users, there is a working mpd plugin.

	All of these can be installed with Pip, and is probably the easiest way.

Running
=======
	Simply run "python WhergBot.py -n" to generate a new configuration file.
	WhergBot will then run with that configuration.

Plugins
=======
	I have *NOT* tested WhergBot on all platforms, therefore some plugins may not work.

	Each plugin requires a 'hooks' dictionary attribute, which contains a regex of the
	command as a key and a list containing the command to call, access level required,
	and a bool for hostchecking.
	For example:

	hooks = { "^@Hi" : [HelloWorld, 5, False] }

	Will hook a "@Hi" command that calls HelloWorld (example below) only
	if the user has level 5 or higher access.

	The function to be called should receive 4 objects:

..

	- A message list, which holds the line sent, so you can parse it for data.
	- A blackbox IRC object, which allows access to sending messages as well as other things.
	- A users object, which allows access to a userlist dict.
	- An allowed object, which gives you access to a dict of access levels.

	For example:

	def HelloWorld(Message, IRC, Users, Allowed):
		IRC.say(Message[3], "Hello {0}!".format(Message[0]))

	This function will send "Hello <Name>" where <Name> is the name of the person who
	triggered the function.

