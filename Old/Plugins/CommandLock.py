#!/usr/bin/env python
from threading import Timer
'''
I decided that I needed some sort of 'control' over Wherg's commands.
So here it is. This 'module' was taken out of Plinko.py itself and placed here.

Usage is simple; Just init a Locker class and call Lock(). Check if the
locker is locked before actually doing anything ofc.

IE:
Locker = Locker(5)
if Locker.Locked:
	return None
else:
	Do_Something()
	Locker.Lock()
'''

'''
Changelog:
March 15:
+ Negative integers lock forever until Unlock() is called, Zero defaults to 5.
+ Return self.Locked after calling.
'''

class Locker(object):
	def __init__(self, Time=None):
		self.Time = Time if Time and type(Time) == int else 5
		# banhammer would be proud ;-;
		self.Locked = False

	def Lock(self):
		if not self.Locked:
			self.Locked = True
			if self.Time > 0:
				t = Timer(self.Time, self.Unlock, ())
				t.daemon = True
				t.start()
		return self.Locked

	def Unlock(self):
		self.Locked = False
		return self.Locked
