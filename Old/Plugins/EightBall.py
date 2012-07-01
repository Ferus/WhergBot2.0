#!/usr/bin/python2
from random import choice

Replies = ["It is certain"
	,"It is decidedly so"
	,"Without a doubt"
	,"Yes - definitely"
	,"You may rely on it"
	,"As I see it yes"
	,"Most likely"
	,"Outlook good"
	,"Signs point to yes"
	,"Yes"
	,"Reply hazy try again"
	,"Ask again later"
	,"Better not tell you now"
	,"Cannot predict now"
	,"Concentrate and ask again"
	,"Don't count on it"
	,"My reply is no"
	,"My sources say no"
	,"Outlook not so good"
	,"Very doubtful"]

def ball(Msg, Sock, Users, Allowed):
	if not Msg[4].split()[1:]:
		Sock.notice(Msg[0], "Ask me a question bud!")
	else:
		Sock.say(Msg[3], "{0}: {1}".format(Msg[0], choice(Replies)))

hooks = {
	"^@8ball" : [ball, 5, False],
	}
	
helpstring = "@8ball <Question> - Returns a random 8ball response."
