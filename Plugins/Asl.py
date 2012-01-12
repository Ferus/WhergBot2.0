#!/usr/bin/python2
import random

try:
	with open("Plugins/AslPlaces.txt", "r") as _f:
		locations = _f.read().splitlines()
except:
	locations = ['Alabama', 'Alaska', 'American', 'Samoa', 'Arizona', 'Arkansas', 'California', 'Colorado',
		'Connecticut', 'Delaware', 'District of Columbia', 'Florida', 'Georgia', 'Guam', 'Hawaii', 'Idaho',
		'Illinois', 'Indiana', 'Iowa', 'Kansas', 'Kentucky', 'Louisiana', 'Maine', 'Maryland', 'Massachusetts',
		'Michigan', 'Minnesota', 'Mississippi', 'Missouri', 'Montana', 'Nebraska', 'Nevada', 'New Hampshire',
		'New Jersey', 'New Mexico', 'New York', 'North Carolina', 'North Dakota', 'Northern Marianas Islands',
		'Ohio', 'Oklahoma', 'Oregon', 'Pennsylvania', 'Puerto Rico', 'Rhode Island', 'South Carolina',
		'South Dakota', 'Tennessee', 'Texas', 'Utah', 'Vermont', 'Virginia',
		'Virgin Islands', 'Washington', 'West Virginia', 'Wisconsin', 'Wyoming']

def asl(msg, sock, users, allowed):
	sock.say(msg[3], "{0}/{1}/{2}".format(random.randint(1,80), random.choice(['m','f','trans']), random.choice(locations)))

hooks = {
	'(?:\s+?|^)asl(?:\s+?|$)': [asl, 5, False],	
		}

helpstring = "Uses a regex to find \"asl\" in a message, sends a \"random\" asl."
