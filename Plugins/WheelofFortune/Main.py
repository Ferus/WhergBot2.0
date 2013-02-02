from . import WoF

class WhergWoFWrapper(object):
    def __init__(self):
        self.WoFGame = WoF.WheelofFortune()

    def setCategory(self, data):
        category = " ".join(text[1:]).strip()
        if category == "":
            autoCategory = random.choice(list(Solutions.solutions.keys()))
            game.setCategory(autoCategory)
            gameInstance.setSolution(random.choice(Solutions.solutions[autoCategory]))
            self.IRC.say(data[2], "The category is \""+game.getCategory()+"\". The solution has been set to an item of this category.")
        else:
            game.setCategory(category)
            self.IRC.say(data[2], "Category Chosen: "+autoCategory if autoPick else category)

    def setSolution(self, data):
        # Don't use this if using an autoPicked Category
        self.WoFGame.setSolution(" ".join(text[1:]).strip())
        self.IRC.say(data[2], self.WoFGame.getSolution())

    def addPlayers(self, data):
        # make a list here, then give it to self.WoFGame.setPlayers() when starting
        pass

    def start(self, data):
        self.WoFGame.setPlayers(self.playerList)

    def spin(self, data):
        self.WoFGame.wheelSpin()
        spindata = self.WoFGame.wheelValue
        self.IRC.say(data[2], "\x03{0}{1}{2}\x03".format(spindata[1],spindata[2],spindata[0]))

    def guess(self, data):
        pass

class Main(WhergWoFWrapper):
    def __init__(self, Name, Parser):
        WhergWoFWrapper.__init__(self)
        self.__name__ = Name
        self.Parser = Parser
        self.IRC = self.Parser.IRC

    def Load(self):
        self.Parser.hookCommand("PRIVMSG", self.__name__, {"^@WoFroll$": self.spin,
            "^@WoFsetC \d{1,}$": self.setCategory,
            "^@WoFsetS \d{1,}$": self.setSolution,
            "^@WoFjoin": self.joinWoF,
            "^@WoFguess \d{1,}$": self.guess,
            "^@WoFplay": self.start})

    def Unload(self):
        pass

    def Reload(self):
        pass
