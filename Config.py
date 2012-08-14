#!/usr/bin/env python
Global = {
	"unwantedchars": "\x03(?:[0-9]{1,2})?(?:,[0-9]{1,2})?|\x02|\x07|\x1F"
	,"timeformat": "[%H:%M:%S] >>"
	}

Servers = {
	"DatNode":
		{"host": "opsimathia.datnode.net"
		,"port": 6697
		,"nick": "WhergBot|T"
		,"realname": "WhergBot 2.0 [Ferus]"
		,"ident": "Wherg"
		,"channels": "#hacking,#4chon,#feels,#bots,#omegle,#games"
		,"ssl": True
		,"enabled": True
		,"quitmessage": "h"

		,"owner": {"nicks": ["Ferus", "Ferrous", "^"]
			,"hosts": ["the.interwebs", "ur.messages"]
			,"idents": ["anonymous", "carroting"]
		}
	}
	,"n0v4":
		{"host": "irc.n0v4.com"
		,"port": 6697
		,"nick": "WhergBot"
		,"realname": "WhergBot 2.0 [Ferus]"
		,"ident": "Wherg"
		,"channels": "#bots,#omegle"
		,"ssl": True
		,"enabled": False
		,"quitmessage": "h"

		,"owner": {"nicks": ["Ferus", "Ferrous"]
			,"hosts": ["the.interwebs"]
			,"idents": ["anonymous"]
		}
	}
}

