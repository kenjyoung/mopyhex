import sys
from mctsagent import mctsagent
from gamestate import gamestate
class gtpinterface:
	"""
	Interface for using go-text-protocol to control the program
	Each implemented GTP command returns string response for the user.
	The interface contains an agent which decides which moves to make on request
	along with a gamestate which holds the current state of the game.
	"""
	def __init__(self, agent):
		commands={}
		commands["name"] = self.gtp_name
		commands["version"] = self.gtp_version
		commands["known_command"] = self.gtp_known
		commands["list_commands"] = self.gtp_list
		commands["quit"] = self.gtp_quit
		commands["boardsize"] = self.gtp_boardsize
		commands["clear_board"] = self.gtp_clear
		commands["play"] = self.gtp_play
		commands["genmove"] = self.gtp_genmove
		commands["showboard"] =self.gtp_show
		self.commands = commands
		self.agent = agent
		self.game = gamestate(8)

	def send_command(self, command):
		parsed_command = command.split()
		#first word specifies function to call, the rest are args
		name = parsed_command[0]
		args = parsed_command[1:]
		if(name in self.commands):
			return self.commands[name](args)
		else:
			return "Unrecognized command"
	def gtp_name(self, args):
		return "Mopyhex"

	def gtp_version(self, args):
		return ""

	def gtp_known(self, args):
		if(len(args)<1):
			return "Not enough arguments"
		if(args[0] in commands):
			return "Command known"
		else:
			return "Command unknown"

	def gtp_list(self, args):
		ret=""
		for command in self.commands:
			ret+=command+'\n'
		return ret

	def gtp_quit(self, args):
		sys.exit()

	def gtp_boardsize(self, args):
		return ""

	def gtp_clear(self, args):
		return ""

	def gtp_play(self, args):
		return ""

	def gtp_genmove(self, args):
		return ""

	def gtp_show(self, args):
		return str(self.game)
