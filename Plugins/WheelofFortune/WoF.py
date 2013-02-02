#!/usr/bin/env python

# Python 2 support
from __future__ import print_function

import sys
import operator
import random

from . import Solutions

class WoFWheel(object):
    def __init__(self):
        self.wheelChoices = [
            # Based on the Round 4 wheel seen on the US version of
            # Wheel Of Fortune during it's 30th season

            # Amount, chance(1-10), foreground colour, background colour
            # 0: bankrupt. -1: lose a turn. -2. free play
            (5000,  3, "01", "15"),#grey
            ( 500, 10, "01", "03"),#green
            ( 900,  8, "01", "08"),#yellow
            ( 700,  9, "01", "04"),#red
            ( 300,  8, "01", "11"),#sky blue
            ( 800,  8, "01", "07"),#orange
            ( 550, 10, "01", "06"),#purple
            ( 400,  7, "01", "08"),#yellow
            ( 500,  9, "01", "13"),#pink
            ( 600,  7, "01", "04"),#red
            ( 350, 10, "01", "11"),#sky blue
            ( 500, 10, "01", "09"),#lime green
            ( 900,  7, "01", "13"),#pink

            # Bankrupt
            # Also lose a turn
            (   0,  2, "00", "01"),#black, white text
            
            ( 650, 10, "01", "06"),#purple

            # Free Play
            # Allows a contestant to call a free vowel or a consonant at
            # $500 per occurrence, or solve the puzzle, with no penalty for
            # a wrong letter or solution.
            (  -2,  5, "01", "16"),#rainbow this thing

            ( 700, 10, "01", "11"),#sky blue

            # Lose a Turn
            (  -1,  2, "01", "00"),#white

            ( 800, 10, "01", "04"),#red
            ( 500,  6, "01", "06"),#purple
            ( 450,  7, "01", "13"),#pink
            ( 500,  5, "01", "03"),#green
            ( 300,  4, "01", "07"),#orange
            (   0,  2, "00", "01")]#black, white text

        self.weightedWheelChoices = []
        for i in range(len(self.wheelChoices)):
            for weightNumber in range(self.wheelChoices[i][1]):
                for x in range(weightNumber):
                    self.weightedWheelChoices.append((
                        self.wheelChoices[i][0],
                        self.wheelChoices[i][2],
                        self.wheelChoices[i][3]))

    def spin(self):
        ''' Returns value, foreground color, background color '''
        return random.choice(self.weightedWheelChoices)

class WoFGuessingGame(object):
    def __init__(self, solution):
        self.solution = solution.lower()

        self.lettersLeft = len(self.solution)
        for character in " &-.'":
            self.lettersLeft -= self.solution.count(character)

        self.letterCount = {}
        for character in self.solution:
            if character not in " &-.'":
                if character in self.letterCount:
                    self.letterCount[character] += 1
                else:
                    self.letterCount[character] = 1

        self.guessedLetters = ""

    def guessLetter(self, letter):
        self.guessedLetters += letter
        if letter in self.letterCount:
            letterCount = self.letterCount[letter]
            self.lettersLeft -= self.letterCount[letter]
            self.letterCount[letter] = 0
            return (letter, letterCount)
        else:
            return (letter, 0)

    def guessSolution(self, solution):
        if self.solution == solution:
            return True
        else:
            return False

    def getPuzzle(self):
        outSolution = self.solution
        for letter in self.letterCount:
            if self.letterCount[letter] > 0:
                outSolution = outSolution.replace(letter,"_")
        return outSolution

class WheelofFortune(object):
    def __init__(self):
        self.autoCategory = False
        self.wheel = WoFWheel()
        self.wheelValue = []
        self.skipTurn = []

    # Getters and setters because.
    def setCategory(self, category):
        self.autoCategory = False
        self.solutionCategory = category

    def setCategoryRandom(self):
        self.autoCategory = True
        self.solutionCategory = random.choice(list(Solutions.solutions.keys()))

    def getCategory(self):
        return self.solutionCategory

    def setSolution(self, solution):
        self.guessingGame = WoFGuessingGame(solution)

    def setSolutionRandom(self):
        self.guessingGame = WoFGuessingGame(random.choice(Solutions.solutions[self.getCategory()]))

    def getSolution(self):
        return self.guessingGame.solution

    def getLettersLeft(self):
        return self.guessingGame.lettersLeft

    def getGuessedLetters(self):
        return self.guessingGame.guessedLetters

    def getPuzzle(self):
        return self.guessingGame.getPuzzle()

    def setPlayers(self, playerList):
        self.playerList = []
        for player in playerList:
            self.playerList.append([player,0])
        self.playerTurn = playerList[0]

    def getPlayers(self):
        return [player[0] for player in self.playerList]

    def setPlayerMoney(self, amount):
        for playerData in self.playerList:
            if self.playerTurn == playerData[0]:
                self.playerList[self.playerList.index(playerData)][1] = amount
    
    def skipPlayerTurn(self):
        for playerData in self.playerList:
            if self.playerTurn == playerData[0]:
                self.skipTurn.append(self.playerList[self.playerList.index(playerData)][0])
    
    def wheelSpin(self):
        self.wheelValue = self.wheel.spin()

    def incTurn(self):
        try:
            for playerData in self.playerList:
                if self.playerTurn == playerData[0]:
                    self.playerTurn = self.playerList[self.playerList.index(playerData)+1][0]
                    break
        except IndexError:
            self.playerTurn = self.playerList[0][0]
        if self.playerTurn in self.skipTurn:
            self.skipTurn.remove(self.playerTurn)
            self.incTurn()

    def guess(self, guess):
        # Messy, but it works. Should fix up anyway.
        if len(guess) == 1:
            numOfGuessedLettersinSolution = self.guessingGame.guessLetter(guess)[1]
            for playerData in self.playerList:
                if self.playerTurn == playerData[0]:
                    if numOfGuessedLettersinSolution > 0:
                        if self.wheelValue[0] > 0: #Normal
                            # Buying vowels for 250
                            if guess in "aeiou":
                                self.playerList[self.playerList.index(playerData)][1] -= 250
                            self.playerList[self.playerList.index(playerData)][1] += numOfGuessedLettersinSolution * self.wheelValue[0]
                        elif self.wheelValue[0] == -2: #Free play:
                            # Vowels are free; every correct letter gets 500
                            self.playerList[self.playerList.index(playerData)][1] += numOfGuessedLettersinSolution * 500
                        return numOfGuessedLettersinSolution
                    if numOfGuessedLettersinSolution == 0:
                        if self.wheelValue[0] > 0 and guess in "aeiou": #Normal
                            self.playerList[self.playerList.index(playerData)][1] -= 250
                        self.incTurn()
                        return 0
        elif len(guess) > 1:
            isSolved = self.guessingGame.guessSolution(guess)
            if isSolved == True:
                for playerData in self.playerList:
                    if self.playerTurn == playerData[0]:
                        for letter in self.guessingGame.letterCount:
                            self.playerList[self.playerList.index(playerData)][1] += self.guessingGame.letterCount[letter] * self.wheelValue[0]
                            self.guessingGame.letterCount[letter] = 0
                self.guessingGame.letterCount.clear()
                self.guessingGame.lettersLeft = 0
                return -1
            else:
                self.incTurn()
                return 0
        else:
            self.incTurn()
            return 0

def main():
    gameInstance = WheelofFortune()

    def Spin():
        print("It is now {player}'s turn.".format(player=gameInstance.playerTurn))
        print("Spin Amount: ", end="")
        gameInstance.wheelSpin()
        if gameInstance.wheelValue[0] == 0:
            print("Bankrupt\n")
            gameInstance.setPlayerMoney(0)
            gameInstance.skipPlayerTurn()
            gameInstance.incTurn()
            Spin()
        elif gameInstance.wheelValue[0] == -1:
            print("Lose A Turn\n")
            gameInstance.skipPlayerTurn()
            gameInstance.incTurn()
            Spin()
        elif gameInstance.wheelValue[0] == -2:
            print("Free Play")
        else:
            print(str(gameInstance.wheelValue[0]))
    
    def printPlayerMoney():
        for player in gameInstance.playerList:
            print("{player} has ${money}.".format(player=player[0], money=player[1]))
    
    autoPick = False
    if sys.version_info.major > 2:
        category = input("Category: ")
    else:
        category = raw_input("Category: ")
        
    if category == "":
        autoPick = True
        autoCategory = random.choice(list(Solutions.solutions.keys()))
        gameInstance.setCategory(autoCategory)
    else:
        gameInstance.setCategory(category)
    print("Category Chosen: {category}".format(category=(autoCategory if autoPick else category)))

    if autoPick == True:
        gameInstance.setSolution(random.choice(Solutions.solutions[autoCategory]))
    else:
        if sys.version_info.major > 2:
            gameInstance.setSolution(input("Solution: "))
        else:
            gameInstance.setSolution(raw_input("Solution: "))

    #print("Solution: "+gameInstance.getSolution())

    print("At least two players are required. Enter blank name when done.")
    playerList = []
    while True:
        if sys.version_info.major > 2:
            player = input("Add Player Name: ")
        else:
            player = raw_input("Add Player Name: ")
        if player == "":
            break
        playerList.append(player) if player not in playerList else print("That player already exists!")
    if len(playerList) < 2:
        print("Fewer than two players. Quitting...")
        sys.exit(0)
    gameInstance.setPlayers(playerList)
    print("Players: "+", ".join(gameInstance.getPlayers()))

    # Or: x = WheelOfFortune("Category","Solution",["Player1","Player2"])

    print()
    while gameInstance.getLettersLeft() > 0:
        if gameInstance.getLettersLeft() > 1:
            print("There are {letters} letters left.".format(letters=gameInstance.getLettersLeft()))
        else:
            print("There is 1 letter left.")
        print("Puzzle: {puzzle}".format(puzzle=gameInstance.getPuzzle()))
        
        Spin()

        print(gameInstance.playerTurn, end="")
        if sys.version_info.major > 2:
            guess = input("'s guess: ")
        else:
            guess = raw_input("'s guess: ")
        lettersGuessedCorrectly = gameInstance.guess(guess)
        #print("guess length: "+str(len(guess))+" correct: "+str(lettersGuessedCorrectly))
        if len(guess) == 1 and lettersGuessedCorrectly > 1:
            print("There are {0} {1}'s.".format(lettersGuessedCorrectly, guess))
        elif len(guess) == 1 and lettersGuessedCorrectly == 1:
            print("There is one {0}.".format(guess))
        elif len(guess) == 1 and lettersGuessedCorrectly == 0:
            print("There are no {0}s.".format(guess))
        elif len(guess) > 1 and lettersGuessedCorrectly == -1:
            print("{0} has correctly guessed the solution!".format(gameInstance.playerTurn))
        printPlayerMoney()
        print()
        
    else:
        print("\"{solution}\" is the solution.".format(solution=gameInstance.getSolution()))
        playerList = sorted(gameInstance.playerList,key=operator.itemgetter(1), reverse=True)
        highestValue = playerList[0][1]
        winners = []
        #print(str(playerList))
        for player in playerList:
            if player[1] == highestValue:
                winners.append(player[0])
        #print(str(winners))
        if len(winners) == 1:
            print("{player} has won with ${money}!".format(player=winners[0], money=highestValue))
        else:
            print("{players} have tied with ${money}!".format(players=", ".join(winners), money=highestValue))

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
        sys.exit(0)
