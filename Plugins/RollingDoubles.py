#!/usr/bin/python2
from random import randint

def roll():
	return "".join([randint(0,6), randint(0,6)])

hooks = {
	'^@doubles': [roll, 5, False],
}

helpstring = "Get your doubles here"
