#!/usr/bin/env python
Global = {
	"unwantedchars": "\x03(?:[0-9]{1,2})?(?:,[0-9]{1,2})?|\x02|\x07|\x1F"
	,"timeformat": "[%H:%M:%S] >>"
	,"owner": {"nicks": ["Ferus"]
		,"hosts": ["the.interwebs"]
		,"idents": ["anonymous"]
		}
}

Servers = {
	"DatNode":
		{"host": "opsimathia.datnode.net"
		,"port": 6697
		,"nick": "WhergBot"
		,"realname": "WhergBot 2.0 [Ferus]"
		,"ident": "Wherg"
		,"channels": "#hacking,#4chon,#feels,#bots,#omegle,#games"
		,"logging": False
		,"logfile": "DatNode.log"
		,"ssl": True
		,"enabled": True
		,"quitmessage": "h"
		}
	
	,"n0v4":
		{"host": "irc.n0v4.com"
		,"port": 6697
		,"nick": "WhergBot"
		,"realname": "WhergBot 2.0 [Ferus]"
		,"ident": "Wherg"
		,"channels": "#bots,#omegle"

		,"logging": False
		,"logfile": "n0v4.log"
		,"ssl": True
		,"enabled": False
		,"quitmessage": "h"
		}
	}

