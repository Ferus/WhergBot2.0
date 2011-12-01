#!/usr/bin/python2

import Core

nick = 'WhergBot' #Bots Nickname
real = 'WhergBot [Ferus]' #Bots realname
ident = 'Wherg' #Bots Ident
password = 'LOLiTROLLu' #Bots Nickserv pass
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
		WhergBot.irc.join("#hacking,#lobby,#4chon,#circlejerk,#tinyboard,#animu")
		if password:
			WhergBot.Identify(password)
		while WhergBot.irc._isConnected:
			WhergBot.Parse(WhergBot.irc.recv(bufferlen=1024))
		else:
			WhergBot.irc.close()
			quit()
			
	except KeyboardInterrupt:
		print("\n* [Core] Interrupt Caught; Quitting!")
		WhergBot.p.command.Quit("KeyboardInterrupt Caught!")
