import json
import urllib.request

class Main(object):
	def __init__(self, Name, Parser):
		self.__name__ = Name
		self.Parser = Parser
		self.IRC = self.Parser.IRC
		self.url = "https://whatstatus.info/json.php"

	def getStatus(self, data):
		statusdata = json.loads(urllib.request.urlopen(self.url).read().decode("utf-8"))
		self.IRC.say(data[2],
			"What.CD Status: " + 
			"Site: " + ("\x0303UP\x03 " if statusdata["status"]["site"] == "up" else "\x0305DOWN\x03 ") +
			"Tracker: " + ("\x0303UP\x03 " if statusdata["status"]["tracker"] == "up" else "\x0305DOWN\x03 ") +
			"IRC: " + ("\x0303UP\x03 " if statusdata["status"]["irc"] == "up" else "\x0305DOWN\x03 ")
		)

	def Load(self):
		self.Parser.hookCommand(
			"PRIVMSG", self.__name__, {"^@what$": self.getStatus}
		)

	def Unload(self):
		pass

	def Reload(self):
		pass
