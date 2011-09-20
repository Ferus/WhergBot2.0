#!/usr/bin/python2

import Core

nick = 'WhergBot2' #Bots Nickname
real = 'WhergBot [Ferus]' #Bots realname
ident = 'Wherg' #Bots Ident
owner = ['Ferus', 'anonymous@the.interwebs', 0] #Bots owner, [Nick, Ident@Host, Access Level]

if __name__ == '__main__':
	try:
		WhergBot = Core.Bot(nick, real, ident, owner)
		WhergBot.Connect('opsimathia.datnode.net')
		WhergBot.Join("hacking")
		while WhergBot.irc._isConnected:
			msg = WhergBot.Parse(WhergBot.irc.recv(bufferlen=1024))
			print(msg)
			
	except KeyboardInterrupt:
		print("\nInterrupt Caught; Quitting!")
		WhergBot.irc.close()
		quit()
		


