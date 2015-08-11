from mctsagent import *

class crit_mctsagent(mctsagent):
	def __init__(self, state=gamestate(8)):
		super().__init__(state)
		self.crit_pts = set()

	def find_crit(self,state):
		return set()

	def roll_out(self, state):
		"""Simulate a random game except that we play all known critical
		cells first, return the winning player and record critical cells at the end."""
		moves = [x for x in self.crit_pts if state.board[x] == gamestate.PLAYERS["none"]]
		last = None
		while(moves):
			move = random.choice(moves)
			state.play(move)
			moves.remove(move)
			if(state.winner() != gamestate.PLAYERS["none"]):
				last = move
				break

		if(state.winner() == gamestate.PLAYERS["none"]):
			while(True):
				moves = state.moves()
				move = random.choice(moves)
				state.play(move)
				moves.remove(move)
				if(state.winner() != gamestate.PLAYERS["none"]):
					last = move
					break

		if(last):
			self.crit_pts.|=find_crit(state)

		return state.winner()

