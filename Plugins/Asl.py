import random
def asl(msg, sock):
	locations = ['nigeria','aus','cali','nyc','nsw','fl','uk','france','russia','germany','japan','china','nz']
	sock.say(msg[3], "{0}/{1}/{2}".format(random.randint(1,100), random.choice(['m','f','trans']), random.choice(locations)))

hooks = {
	'asl': [asl, 5, False],	
		}
