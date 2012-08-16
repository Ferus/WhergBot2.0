#!/usr/bin/env python
Global = {
	"unwantedchars": "\x03(?:[0-9]{1,2})?(?:,[0-9]{1,2})?|\x02|\x07|\x1F"
	,"timeformat": "[%H:%M:%S] >>"
	}

Servers = {
	"DatNode":
		{"host": "opsimathia.datnode.net"
		,"port": 6697
		,"nick": "WhergBot|Test"
		,"realname": "WhergBot 2.0 [Ferus]"
		,"ident": "Wherg"
		,"channels": "#hacking"
		,"ssl": True
		,"enabled": True
		,"quitmessage": "h"
		,"plugins": ['Services'
			,'Oper'
			,'Plinko'
			,'Omegle'
			,'Misc'
			,'Quit'
			,'Matix'
			,'Fapget'
			,'GuessingGame'
			,'PyFileServ'
			,'Quotes'
			,'EightBall'
			,'Wikipedia'
			,'Told'
			,'Uptime'
			,'SloganMaker'
			,'Exec'
			,'Asl'
			,'Meme'
			,'Etymology'
			,'Slap'
			,'YouTube'
			,'Tinyboard'
			,'Ermahgerd'
#			,'Wordnik'
			,'UrbanDictionary'
			,'InsultGenerator'
			,'FuckMyLife'
			,'Imgur'
			,'General'
			,'PyMpd']
		,"owner": {"nicks": ["Ferus", "Ferrous", "^"]
			,"hosts": ["the.interwebs", "ur.messages"]
			,"idents": ["anonymous", "carroting"]
		}
	}

	,"n0v4":
		{"host": "irc.n0v4.com"
		,"port": 6697
		,"nick": "WhergBot|T"
		,"realname": "WhergBot 2.0 [Ferus]"
		,"ident": "Wherg"
		,"channels": "#bots"
		,"ssl": True
		,"enabled": False
		,"quitmessage": "h"
		,"plugins": ['Services'
			,'Oper'
			,'Plinko'
			,'Omegle'
			,'Misc'
			,'Quit'
			,'Matix'
			,'Fapget'
			,'GuessingGame'
			,'PyFileServ'
			,'Quotes'
			,'EightBall'
			,'Wikipedia'
			,'Told'
			,'Uptime'
			,'SloganMaker'
			,'Exec'
			,'Asl'
			,'Meme'
			,'Etymology'
			,'Slap'
			,'YouTube'
			,'Tinyboard'
			,'Ermahgerd'
#			,'Wordnik'
			,'UrbanDictionary'
			,'InsultGenerator'
			,'FuckMyLife'
			,'Imgur'
			,'General'
			,'PyMpd']
		,"owner": {"nicks": ["Ferus", "Ferrous"]
			,"hosts": ["the.interwebs"]
			,"idents": ["anonymous"]
		}
	}

	,"DatNodeGentBot":
		{"host": "mempsimoiria.datnode.net"
		,"port": 6697
		,"nick": "gentbot|h"
		,"realname": "gentbot 2.0 [Ferus]"
		,"ident": "gentbot"
		,"channels": "#hacking"
		,"ssl": True
		,"enabled": False
		,"quitmessage": 'h'
		,"plugins": ['General', 'Gentbot']
		,"owner": {"nicks": ["Ferus"]
			,"hosts": ["the.interwebs"]
			,"idents": ["anonymous"]
			}
	}
}

