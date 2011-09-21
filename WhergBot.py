#!/usr/bin/python2

import Core

nick = 'WhergBot2' #Bots Nickname
real = 'WhergBot [Ferus]' #Bots realname
ident = 'Wherg' #Bots Ident
owner = ['Ferus', 'anonymous@the.interwebs', 0] #Bots owner, [Nick, Ident@Host, Access Level]
ssl = True #To encrypt, Or to not encrypt, That is the question!
if ssl:
	port = 6697 #Our ssl port to use.
else:
	port = 6667 #Our non-ssl port.

if __name__ == '__main__':
	try:
		WhergBot = Core.Bot(nick, real, ident, owner, ssl)
		WhergBot.Connect(server='opsimathia.datnode.net', port=port)
		WhergBot.Join("hacking")
		while WhergBot.irc._isConnected:
			msg = WhergBot.Parse(WhergBot.irc.recv(bufferlen=1024))
			print(msg)
			
	except KeyboardInterrupt:
		print("\nInterrupt Caught; Quitting!")
		WhergBot.irc.quit("KeyboardInterrupt Caught!")
		WhergBot.irc.close()
		quit()
		


