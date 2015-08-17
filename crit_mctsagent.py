from mctsagent import *

class crit_node(node):
	def __init__(self, move = None, parent = None):
		"""
		Initialize a new node with optional move and parent and initially empty
		children list and rollout statistics and unspecified outcome.
		"""
		self.move = move
		self.parent = parent
		self.N = 0 #times this position was visited
		self.Q = 0 #average reward (wins-losses) from this position
		self.Q_CRIT = 0 # times this move has been critical in a rollout
		self.N_CRIT = 0 # times this move has appeared in a rollout
		self.children = {}
		self.outcome = gamestate.PLAYERS["none"]

	def add_children(self, children):
		for child in children:
			self.children[child.move] = child

	def value(self, explore, crit):
		"""
		Calculate the UCT value of this node relative to its parent, the parameter
		"explore" specifies how much the value should favor nodes that have
		yet to be thoroughly explored versus nodes that seem to have a high win
		rate. 
		Currently explore is set to zero when choosing the best move to play so
		that the move with the highest winrate is always chossen. When searching
		explore is set to EXPLORATION specified above.
		"""
		#unless explore is set to zero, maximally favor unexplored nodes
		if(self.N == 0):
			if(explore == 0):
				return 0
			else:
				return inf
		else:
			#rave like use of criticality info:
			alpha = max(0,(crit - self.N)/crit)
			return self.Q*(1-alpha)/self.N+self.Q_CRIT*alpha/self.N


class crit_mctsagent(mctsagent):
	CRIT_FACTOR = 500

	def __init__(self, state=gamestate(8)):
		super().__init__(state)
		self.crit_pts = set()


	def best_move(self):
		"""
		Return the best move according to the current tree.
		"""
		if(self.rootstate.winner() != gamestate.PLAYERS["none"]):
			return gamestate.GAMEOVER

		#choose the move of the most simulated node breaking ties randomly
		max_value = max(self.root.children.values(), key = lambda n: n.N).N
		max_nodes = [n for n in self.root.children.values() if n.N == max_value]
		bestchild = random.choice(max_nodes)
		return bestchild.move

	def move(self, move):
		"""
		Make the passed move and update the tree approriately.
		"""
		if move in self.root.children:
			child = self.root.children[move]
			child.parent = None
			self.root = child
			self.rootstate.play(child.move)
			return

		#if for whatever reason the move is not in the children of
		#the root just throw out the tree and start over
		self.rootstate.play(move)
		self.root = crit_node()

	def search(self, time_budget):
		"""
		Search and update the search tree for a specified amount of time in secounds.
		"""
		startTime = time.clock()
		num_rollouts = 0
		total_crits = 0

		#do until we exceed our time budget
		while(time.clock() - startTime <time_budget):
			node, state = self.select_node()
			turn = state.turn()
			if node.parent:
				crit_pts = [x.move for x in node.parent.children.values() if x.Q_CRIT>0]
			else:
				crit_pts = []
			outcome, new_crit, non_crits = self.roll_out(state, crit_pts)
			self.backup(node, turn, outcome, new_crit, non_crits)
			if new_crit:
				total_crits+=1
			num_rollouts += 1

		stderr.write("Avg cut points per rollout: "+str(total_crits/num_rollouts)+"\n")
		stderr.write("Ran "+str(num_rollouts)+ " rollouts in " +\
			str(time.clock() - startTime)+" sec\n")
		stderr.write("Node count: "+str(self.tree_size())+"\n")

	def select_node(self):
		"""
		Select a node in the tree to preform a single simulation from.
		"""
		node = self.root
		state = deepcopy(self.rootstate)

		#stop if we find reach a leaf node
		while(len(node.children)!=0):
			max_value = max(node.children.values(), key = lambda n: n.value(self.EXPLORATION, self.CRIT_FACTOR)).value(self.EXPLORATION, self.CRIT_FACTOR)
			#decend to the maximum value node, break ties at random
			max_nodes = [n for n in node.children.values() if n.value(self.EXPLORATION, self.CRIT_FACTOR) == max_value]
			node = random.choice(max_nodes)
			state.play(node.move)

			#if some child node has not been explored select it before expanding
			#other children
			if node.N == 0:
				return (node, state)

		#if we reach a leaf node generate its children and return one of them
		#if the node is terminal, just return the terminal node
		if(self.expand(node, state)):
			node = random.choice(list(node.children.values()))
			state.play(node.move)
		return (node, state)


	def backup(self, node, turn, outcome, crit, non_crits):
		"""
		Update the node statistics on the path from the passed node to root to reflect
		the outcome of a randomly simulated playout.
		"""
		#note that reward is calculated for player who just played
		#at the node and not the next player to play
		reward = -1 if outcome == turn else 1

		while node!=None:
			if crit in node.children:
					node.children[crit].Q_CRIT+=1
					node.children[crit].N_CRIT+=1
			for point in non_crits:
				if point in node.children:
					node.children[point].N_CRIT+=1
			node.N += 1
			node.Q +=reward
			reward = -reward
			node = node.parent

	def expand(self, parent, state):
		"""
		Generate the children of the passed "parent" node based on the available
		moves in the passed gamestate and add them to the tree.
		"""
		children = []
		if(state.winner() != gamestate.PLAYERS["none"]):
		#game is over at this node so nothing to expand
			return False


		for move in state.moves():
			children.append(crit_node(move, parent))

		parent.add_children(children)
		return True

	def set_gamestate(self, state):
		"""
		Set the rootstate of the tree to the passed gamestate, this clears all
		the information stored in the tree since none of it applies to the new 
		state.
		"""
		self.rootstate = deepcopy(state)
		self.root = crit_node()

	def roll_out(self, state, crit_pts):
		"""Simulate a random game except that we play all known critical
		cells first, return the winning player and record critical cells at the end."""
		"""moves = [x for x in crit_pts if state.board[x] == gamestate.PLAYERS["none"]]
		last = None
		while(moves):
			move = random.choice(moves)
			state.play(move)
			moves.remove(move)
			if(state.winner() != gamestate.PLAYERS["none"]):
				last = move
				break"""

		"""if(state.winner() == gamestate.PLAYERS["none"]):"""
		moves = [x for x in crit_pts if state.board[x] == gamestate.PLAYERS["none"]]
		last = None
		while(moves):
			move = random.choice(moves)
			state.play(move)
			moves.remove(move)
			if(state.winner() != gamestate.PLAYERS["none"]):
				last = move
				break

		if(state.winner() == gamestate.PLAYERS["none"]):
			moves = state.moves()
			while(True):
				move = random.choice(moves)
				state.play(move)
				moves.remove(move)
				if(state.winner() != gamestate.PLAYERS["none"]):
					last = move
					break

		if(last):
			new_crit = last
			non_crits = [(x, y) for x in range(state.size) for y in range(state.size)\
							if state.board[(x,y)]==state.winner() and (x,y)!=last]
		#this only happens if the state the rollout started in was already decided:
		else:
			new_crit = None
			non_crits = None

		return state.winner(), new_crit, non_crits

	def tree_size(self):
		"""
		Count nodes in tree by BFS.
		"""
		Q = Queue()
		count = 0
		Q.put(self.root)
		while not Q.empty():
			node = Q.get()
			count +=1
			for child in node.children.values():
				Q.put(child)
		return count

