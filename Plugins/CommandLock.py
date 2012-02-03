#!/usr/bin/env python
from threading import Timer
'''
I decided that I needed some sort of 'control' over Wherg's commands.
So here it is. This module was taken out of Plinko.py itself and placed here.
'''
class Locker(object):
	def __init__(self, Time=None):
		self.Time = Time if Time and type(Time) == int else 5
		#banhammer would be proud ;-;
		self.Locked = False
			
	def Lock(self):
		if not self.Locked:
			self.Locked = True
			t = Timer(self.Time, self.Unlock, ())
			t.daemon = True
			t.start()
			
	def Unlock(self):
		self.Locked = False
