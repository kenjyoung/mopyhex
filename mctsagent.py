from gamestate import gamestate
import time
import random
from math import sqrt, log
from copy import copy, deepcopy
from sys import stderr
EXPLORATION = 1
inf = float('inf')

class node:
	"""
	Node for the MCST. Stores the move applied to reach this node from its parent,
	stats for the associated game position, children, parent and outcome 
	(outcome==none unless the position ends the game).
	"""
	def __init__(self, move = None, parent = None):
		self.move = move
		self.parent = parent
		self.N = 0 #times this position was visited
		self.Q = 0 #average reward (wins-losses) from this position
		self.children = []
		self.outcome = gamestate.PLAYERS["none"]

	def add_children(self, children):
		self.children += children

	def set_outcome(self, outcome):
		self.outcome = outcome

	def value(self, explore):
		if(self.N == 0):
			return inf
		else:
			return self.Q/self.N + explore*sqrt(2*log(self.parent.N/self.N))


class mctsagent:
	"""
	Basic no frills implementation of an agent that preforms MCTS for hex.
	"""
	def __init__(self, state):
		self.rootstate = deepcopy(state)
		self.root = node()


	def best_move(self):
		"""
		Return the best move according to the current tree
		"""
		if(self.rootstate.winner() != gamestate.PLAYERS["none"]):
			return gamestate.GAMEOVER
		max_value = max(self.root.children, key = lambda n: n.value(0)).value(0)
		max_nodes = [n for n in self.root.children if n.value(0) == max_value]
		bestchild = random.choice(max_nodes)
		return bestchild.move


	def move(self, move):
		for child in self.root.children:
			if move == child.move:
				child.parent = None
				self.root = child
				self.rootstate.play(child.move)
				return
		#if for whatever reason the move is not in the children of
		#the root just throw out the tree and start over
		self.rootstate.play(move)
		self.root = node()


	def search(self, time_budget):
		startTime = time.clock()
		num_rollouts = 0

		#do until we exceed our time budget
		while(time.clock() - startTime <time_budget):
			node, state = self.select_node()
			outcome = self.roll_out(state)
			self.backup(node, state.turn(), outcome)
			num_rollouts += 1
		stderr.write("Ran "+str(num_rollouts)+ " rollouts in " +\
			str(time.clock() - startTime)+" sec\n")


	def select_node(self):
		node = self.root
		state = deepcopy(self.rootstate)

		#stop if we find reach a terminal node
		while(len(node.children)!=0):
			max_value = max(node.children, key = lambda n: n.value(EXPLORATION)).value(EXPLORATION)
			max_nodes = [n for n in node.children if n.value(EXPLORATION) == max_value]
			node = random.choice(max_nodes)
			state.play(node.move)

			#if some child node has not been explored select it before expanding
			#other children
			if node.N == 0:
				return (node, state)

		#if we reach a terminal node generate its children and return one of them
		(node, state) = self.expand(node, state)
		return (node, state)


	def roll_out(self, state):
		moves = state.moves()

		while(state.winner() == gamestate.PLAYERS["none"]):
			move = random.choice(moves)
			state.play(move)
			moves.remove(move)

		return state.winner()


	def backup(self, node, turn, outcome):
		reward = -1 if outcome == turn else 1

		while node!=None:
			node.N += 1
			node.Q +=reward
			reward = -reward
			node = node.parent

		
	def expand(self, parent, state):
		children = []
		if(state.winner() != gamestate.PLAYERS["none"]):
		#game is over at this node so nothing to expand
			return (parent, state)


		for move in state.moves():
			children.append(node(move, parent))

		parent.add_children(children)
		selected_child = random.choice(children)
		state.play(selected_child.move)
		return (selected_child, state)


	def set_gamestate(self, state):
		self.rootstate = deepcopy(state)
		self.root = node()
