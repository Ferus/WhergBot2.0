from . import WoF

class WhergWoFWrapper(object):
    def __init__(self):
        self.WoFGame = WoF.WheelofFortune()
        self.categorySet = False
        self.playerList = []

    def setCategory(self, data):
        category = " ".join(data[4:]).strip()
        if category == "":
            self.WoFGame.setCategoryRandom()
            self.WoFGame.setSolutionRandom()
            self.IRC.say(data[2], "The category is {0}. The solution has been set to an item of this category.".format(self.WoFGame.getCategory()))
            self.IRC.say(data[2], "Solution: "+self.WoFGame.getSolution())
        else:
            self.WoFGame.setCategory(category)
            self.IRC.say(data[2], "Category Chosen: "+category)
        self.categorySet = True

    def setSolution(self, data):
        if data[2][0] == "#":
            self.IRC.say(data[2], "Everyone just saw the solution. Send a private message instead.")
        elif self.categorySet == False:
            self.IRC.say(data[2], "No category set. Please set a category before setting a solution.")
        else:
            self.WoFGame.setSolution(" ".join(data[4:]).strip())
            self.IRC.say(data[2], "Solution: "+self.WoFGame.getSolution())

    def addPlayer(self, data):
        nick = data[0].split("!")[0]
        if nick not in self.playerList:
            self.playerList += nick

    def start(self, data):
        if len(self.playerList) < 2:
            self.IRC.say(data[2], "At least two players are required.")
        else:
            self.WoFGame.setPlayers(self.playerList)

    def spin(self, data):
        self.IRC.say(data[2], "It is now {player}'s turn.".format(player=gameInstance.playerTurn))
        self.WoFGame.wheelSpin()
        spindata = self.WoFGame.wheelValue
        if spindata[0] <= 0:
            if spindata[0] == 0:
                spindata[0] = "Bankrupt"
                self.WoFGame.setPlayerMoney(0)
                self.WoFGame.skipPlayerTurn()
                self.WoFGame.incTurn()
                self.spin(data)
            elif spindata[0] == -1:
                spindata[0] = "Lose a turn"
                self.WoFGame.skipPlayerTurn()
                self.WoFGame.incTurn()
                self.spin(data)
            elif spindata[0] == -2:
                spindata[0] = "Free play"
        self.IRC.say(data[2], "Spin Amount: \x03{0},{1}{2}\x03".format(
            spindata[1],spindata[2],spindata[0]
        ))

    def guess(self, data):
        #self.WoFGame.guess(" ".join(text[4:]))
        pass

class Main(WhergWoFWrapper):
    def __init__(self, Name, Parser):
        WhergWoFWrapper.__init__(self)
        self.__name__ = Name
        self.Parser = Parser
        self.IRC = self.Parser.IRC

    def Load(self):
        self.Parser.hookCommand("PRIVMSG", self.__name__, {
            "^@WoFspin$": self.spin,
            "^@WoFsetC(?: \S+)?$": self.setCategory,
            "^@WoFsetS(?: \S+)?$": self.setSolution,
            "^@WoFjoin$": self.addPlayer,
            "^@WoFguess(?: \S+)?$": self.guess,
            "^@WoFstart$": self.start
        })

    def Unload(self):
        pass

    def Reload(self):
        pass
