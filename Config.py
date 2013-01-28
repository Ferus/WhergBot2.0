#!/usr/bin/env python
Global = {
	"unwantedchars": "\x03(?:[0-9]{1,2})?(?:,[0-9]{1,2})?|\x02|\x07|\x1F"
	}

Servers = {
	"DatNode":
		{"host": "mempsimoiria.datnode.net"
		,"port": 6697
		,"nick": "Wherg"
		,"realname": "WhergBot 2.0 [Ferus]"
		,"ident": "Wherg"
		,"channels": "#boats"
		,"ssl": True
		,"enabled": True
		,"quitmessage": "h"
		,"plugins": [
			'Services'
			,'CleverBot'
			,'Omegle'
			,'Oper'
			,'Plinko'
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
			,'Wordnik'
			,'UrbanDictionary'
			,'InsultGenerator'
			,'FuckMyLife'
			,'Imgur'
			,'General'
			,'Weather'
			,'Roulette'
#			,'PyMpd'
			,'WhatStatus'
			]
		,"owner": {"nicks": ["Ferus", "Ferrous", "^"]
			,"hosts": ["the.interwebs", "ur.messages"]
			,"idents": ["anonymous", "carroting"]
		}
	}

	,"GentBot":
		{"host": "mempsimoiria.datnode.net"
		,"port": 6697
		,"nick": "gentbot|h"
		,"realname": "WhergBot 2.0 [Ferus]"
		,"ident": "gentbot"
		,"channels": "#boats"
		,"ssl": True
		,"enabled": True
		,"quitmessage": 'h'
		,"plugins": [
			'General'
			,'GentBot'
			,'Services'
			]
		,"owner": {"nicks": ["Ferus"]
			,"hosts": ["the.interwebs"]
			,"idents": ["anonymous"]
			}
		}
}

