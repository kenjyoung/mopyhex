import sys
from mctsagent import mctsagent
from gamestate import gamestate
version = 0.1
class gtpinterface:
	"""
	Interface for using go-text-protocol to control the program
	Each implemented GTP command returns a string response for the user, along with
	a boolean indicating success or failure in executing the command.
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
		commands["showboard"] = self.gtp_show
		commands["set_time"] = self.gtp_time
		self.commands = commands
		self.game = gamestate(8)
		self.agent = mctsagent(self.game)
		self.move_time = 5

	def send_command(self, command):
		parsed_command = command.split()
		#first word specifies function to call, the rest are args
		name = parsed_command[0]
		args = parsed_command[1:]
		if(name in self.commands):
			return self.commands[name](args)
		else:
			return (False, "Unrecognized command")
	def gtp_name(self, args):
		return (True, "Mopyhex")

	def gtp_version(self, args):
		return (True, str(version))

	def gtp_known(self, args):
		if(len(args)<1):
			return (False, "Not enough arguments")
		if(args[0] in commands):
			return (True, "Command known")
		else:
			return (True, "Command unknown")

	def gtp_list(self, args):
		ret=""
		for command in self.commands:
			ret+=command+'\n'
		return (True, ret)

	def gtp_quit(self, args):
		sys.exit()

	def gtp_boardsize(self, args):
		if(len(args)<1):
			return (False, "Not enough arguments")
		try:
			size = int(args[0])
		except ValueError:
			return (False, "Argument is not a valid size")
		if size<1:
			return (False, "Argument is not a valid size")
		
		self.game = gamestate(size)
		self.agent.set_gamestate(self.game)
		return (True, "Board size set to "+str(size))

	def gtp_clear(self, args):
		self.game = gamestate(self.game.size)
		self.agent.set_gamestate(self.game)
		return (True, "Board cleared")

	def gtp_play(self, args):
		if(len(args)<2):
			return (False, "Not enough arguments")
		try:
			x =	ord(args[1][0].lower())-ord('a')
			y = int(args[1][1:])-1

			if(x<0 or y<0 or x>=self.game.size or y>=self.game.size):
				return (False, "Cell out of bounds")

			if args[0][0].lower() == 'w':
				if self.game.turn() == gamestate.PLAYERS["white"]:
					self.game.play((x,y))
					self.agent.move((x,y))
					return (True, "Move played")
				else:
					self.game.place_white((x,y))
					self.agent.set_gamestate(game)
					return (True, "Out of turn stone placed")

			elif args[0][0].lower() == 'b':
				if self.game.turn() == gamestate.PLAYERS["black"]:
					self.game.play((x,y))
					self.agent.move((x,y))
					return (True, "Move played")
				else:
					self.game.place_black((x,y))
					self.agent.set_gamestate(game)
					return (True, "Out of turn stone placed")
		except ValueError:
			return (False, "Malformed arguments")

	def gtp_genmove(self, args):
		self.agent.search(self.move_time)
		move = self.agent.best_move()
		self.game.play(move)
		self.agent.move(move)
		return (True, chr(ord('A')+move[0])+str(move[1]+1))

	def gtp_time(self, args):
		if(len(args)<1):
			return (False, "Not enough arguments")
		try:
			time = int(args[0])
		except ValueError:
			return (False, "Argument is not a valid time limit")
		if time<1:
			return (False, "Argument is not a valid time limit")
		self.move_time = time
		return (True, "Time limit per move changed")

	def gtp_show(self, args):
		return (True, str(self.game))
