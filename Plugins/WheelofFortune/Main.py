from . import WoF

class WhergWoFWrapper(object):
    def __init__(self):
        self.WoFGame = WoF.WheelofFortune()
        self.categorySet = False

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

    def addPlayers(self, data):
        # make a list here, then give it to self.WoFGame.setPlayers() when starting
        pass

    def start(self, data):
        self.WoFGame.setPlayers(self.playerList)

    def spin(self, data):
        # remember to change:
        # 0: bankrupt. -1: lose a turn. -2. free play
        self.WoFGame.wheelSpin()
        spindata = self.WoFGame.wheelValue
        self.IRC.say(data[2], "\x03{0},{1}{2}\x03".format(spindata[1],spindata[2],spindata[0]))

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
            #"^@WoFjoin": self.joinWoF,
            "^@WoFguess(?: \S+)?$": self.guess,
            "^@WoFplay": self.start
        })

    def Unload(self):
        pass

    def Reload(self):
        pass
