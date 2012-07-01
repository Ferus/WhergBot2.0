Settings = {'allowedchans': ['#games']
	,'phrases': ['YOU DIDN\'T EVEN GET CLOSE, FAGGOT!'
		,'Try again you fucking faggot.'
		,'How about you stop sucking dicks and /try/ to win next time.'
		,'Congratulations, you didn\'t win shit.'
		]
	,'prizes': {
		'1': ["self.IRC.say(data[2], '{0}'.format(random.choice(Settings['phrases'])))"]
		,'2': ["self.IRC.say(data[2], '{0}'.format(random.choice(Settings['phrases'])))"]
		,'3': ["self.IRC.say(data[2], '{0}'.format(random.choice(Settings['phrases'])))"]
		,'4': ["self.IRC.say(data[2], '!tkb {0} 2m You fucking suck.'.format(data[0].split('!')[0]))", "t = Timer(125, self.IRC.invite, (data[0].split('!')[0], data[2],))", "t.daemon = True", "t.start()"]
		,'5': ["self.IRC.op(data[2], data[0].split('!')[0])", "t = Timer(300, self.IRC.deop, (data[2], data[0].split('!')[0],))", "t.daemon = True", "t.start()"]
		,'6': ["self.IRC.say(data[2], '!tkb {0} 2m You fucking suck.'.format(data[0].split('!')[0]))", "t = Timer(125, self.IRC.invite, (data[0].split('!')[0], data[2],))", "t.daemon = True", "t.start()"]
		,'7': ["self.IRC.say(data[2], '{0}'.format(random.choice(Settings['phrases'])))"]
		,'8': ["self.IRC.say(data[2], '{0}'.format(random.choice(Settings['phrases'])))"]
		,'9': ["self.IRC.say(data[2], '{0}'.format(random.choice(Settings['phrases'])))"]
		}
	}

