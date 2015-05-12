from gamestate import gamestate
import time
import random
from math import sqrt, log
from copy import copy, deepcopy
EXPLORATION = 1
inf = float('inf')

class node:
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

	def value(self):
		if(self.N == 0):
			return inf
		else:
			return self.Q/self.N + EXPLORATION*sqrt(2*log(self.parent.N/self.N))


class mctsagent:
	def __init__(self, state):
		self.rootstate = deepcopy(state)
		self.root = node()


	def best_move(self):
		bestchild = max(self.root.children, key = lambda n: n.value())
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

		#do until we exceed our time budget
		while(time.clock() - startTime <time_budget):
			node, state = self.select_node()
			outcome = self.roll_out(state)
			self.backup(node, state.turn(), outcome)


	def select_node(self):
		node = self.root
		state = deepcopy(self.rootstate)

		#stop if we find reach a terminal node
		while(len(node.children)!=0):
			node = max(node.children, key = lambda n: n.value())
			#if some child node has not been explored select it before expanding
			#other children
			state.play(node.move)

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
		reward = 1 if outcome == turn else -1

		while node!=None:
			node.N += 1
			node.Q +=reward
			reward = -reward
			node = node.parent

		
	def expand(self, parent, state):
		children = []
		if(state.winner() != gamestate.PLAYERS["none"]):
		#outcome is decided so nothing to expand
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



