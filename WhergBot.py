#!/usr/bin/python2

import Core
from threading import Timer

nick = 'WhergBot' #Bots Nickname
real = 'WhergBot [Ferus]' #Bots realname
ident = 'Wherg' #Bots Ident
channels = ['#hacking', '#lobby' ,'#4chon' ,'#circlejerk' ,'#tinyboard' ,'#animu', '#games']
#channels = ['#hacking']
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
		if WhergBot.Nickserv.password != '':
			_p = Timer(3, WhergBot.Identify, ())
			_p.daemon = True
			_p.start()
		#for chan in channels:
		#	_t = Timer(5, WhergBot.irc.join, (chan, ))
		#	_t.daemon = True
		#	_t.start()
		#	Core.sleep(.05)
		_t = Timer(5, WhergBot.irc.join, (",".join(channels),))
		_t.daemon = True
		_t.start() 

		while WhergBot.irc._isConnected:
			WhergBot.Parse(WhergBot.irc.recv(bufferlen=1024))
		else:
			WhergBot.irc.close()
			quit()
			
	except KeyboardInterrupt:
		print("\n* [Core] Interrupt Caught; Quitting!")
		WhergBot.p.command.Quit("KeyboardInterrupt Caught!")
