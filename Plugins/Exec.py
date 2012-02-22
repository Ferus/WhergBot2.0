#!/usr/bin/python2

def _Exec(Message, Sock, Users, Allowed):
	x = " ".join(Message[4].split()[1:])
	if x:
		try:
			Sock.say(Message[3], "Your wish is my command master.")
			exec(x)
		except Exception, e:
			Sock.say(Message[3], str(repr(e)))
	else:
		pass

hooks = {
	'^\$exec' : [_Exec, 0, True],
	}

helpstring = """Runs a python statement. Be very careful with this command, and be sure to keep limited access if keeping it loaded."""
