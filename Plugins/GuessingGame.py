#!/usr/bin/python2

from random import randint

class GuessingGame(object):
	def __init__(self):
		self.MaxNum = 250
		self.CurrentNumber = None
		self.GenNumber()

	def GenNumber(self, sock=None, location=None):
		self.CurrentNumber = randint(1, self.MaxNum)
		if sock and location:
			sock.say(location, "Generating new number. Pick from 0-{0}".format(self.MaxNum))

	def SetMaxNum(self, msg, sock, users, allowed):
		try:
			ToSet = int(msg[4].split()[1])
			self.MaxNum = ToSet
			self.GenNumber(sock=sock, location=msg[3])
		except:
			sock.say(msg[3], "I'm sorry {0}, but {1} doesn't seem to be a valid number.".format(msg[0], msg[4].split()[1]))
			
	def CheckGuess(self, msg, sock, users, allowed):
		try:
			UserGuess = int(msg[4].split()[1])
		except:
			sock.say(msg[3], "I'm sorry {0}, but {1} doesn't seem to be a valid number.".format(msg[0], msg[4].split()[1]))
			return None

		if UserGuess > self.MaxNum:
			sock.say(msg[3], "Sorry {0}, but my maximum number is set to {1}.".format(msg[0], self.MaxNum))
			
		elif UserGuess <= 0:
			sock.say(msg[3], "Sorry {0}, but my number cannot be lower than 0.".format(msg[0]))

		elif UserGuess > self.CurrentNumber:
			sock.say(msg[3], "I'm sorry {0}, but my number is lower than that.".format(msg[0]))

		elif UserGuess < self.CurrentNumber:
			sock.say(msg[3], "I'm sorry {0}, but my number is higher than that.".format(msg[0]))

		elif UserGuess == self.CurrentNumber:
			sock.say(msg[3], "Congratulations {0}, You guessed my number!".format(msg[0]))
			self.GenNumber(sock=sock, location=msg[3])

		else:
			pass #Wut.
			
G = GuessingGame()

hooks = {
	'^@guess': [G.CheckGuess, 5, False],
	'^@setguess': [G.SetMaxNum, 3, False],
	}
