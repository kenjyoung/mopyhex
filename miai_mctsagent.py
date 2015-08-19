from mctsagent import *
from miai_gamestate import miai_gamestate

class miai_mctsagent(mctsagent):

		def roll_out(self, state):
			"""
			Simulate an entirely random game from the passed state and return the winning
			player.
			"""
			state = miai_gamestate(state)
			moves = state.moves()

			while(state.miai_winner() == gamestate.PLAYERS["none"]):
				move = random.choice(moves)
				miai_move = state.get_miai(move, gamestate.OPPONENT[state.turn()])
				state.play(move)
				moves.remove(move)
				#if a miai move is associated with the last move played,
				#use that move next instead of picking at random
				while(miai_move!=None):
					move = miai_move
					miai_move = state.get_miai(move, gamestate.OPPONENT[state.turn()])
					state.play(move)
					moves.remove(move)

			return state.miai_winner()