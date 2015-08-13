from mctsagent import *

class ext_crit_mctsagent(mctsagent):
	def __init__(self, state=gamestate(8)):
		super().__init__(state)
		self.crit_pts = set()

	def get_graph(self, state, color):
		graph = {}
		size = state.size
		board = state.board
		if color == gamestate.PLAYERS["white"]:
			groups = state.white_groups
		else:
			groups = state.black_groups

		group_rep = groups.find(gamestate.EDGE1)
		if color == gamestate.PLAYERS["white"]:
			graph[gamestate.EDGE1] = [(0,y) for y in range(size) if  groups.find((0,y))==group_rep]
			graph[gamestate.EDGE2] = [(size-1,y) for y in range(size) if groups.find((size-1,y))==group_rep]
		else:
			graph[gamestate.EDGE1] = [(x,0) for x in range(size) if  groups.find((x,0))==group_rep]
			graph[gamestate.EDGE2] = [(x, size-1) for x in range(size) if groups.find((x,size-1))==group_rep]

		for n in graph[gamestate.EDGE1]:
			graph[n] = [gamestate.EDGE1]
		for n in graph[gamestate.EDGE2]:
			graph[n] = [gamestate.EDGE2]

		for x in range(size):
			for y in range(size):
				if board[(x,y)] == color:
					if groups.find((x,y)) == group_rep:
						if (x,y) not in graph.keys():
							graph[(x,y)] = []
						for n in state.neighbors((x,y)):
							if groups.find(n) == group_rep:
								graph[(x,y)].append(n)

		return graph	

	def find_crit(self, G, s, d):
		cut_points = set()
		S = []
		#stack contains nodes being visited along with iterator into children
		S.append([s ,iter(G[s])])
		visited = set()
		visited.add(s)
		leaves = []
		depth = {}
		depth[s] = 0
		parent = {}
		parent[s] = None
		low = {}
		low[s] = 0

		while S:
			v = S[-1][0]
			try:
				child = next(S[-1][1])
				#vertex is initially pushed to stack
				if(child not in visited):
					visited.add(child)
					S.append([child ,iter(G[child])])
					depth[child] = depth[v]+1
					parent[child] = v
					low[child] = depth[child]
				elif child is not parent[v]:
					low[v] = min(low[v], depth[child])
			#vertex is removed from stack and we backtrack
			except StopIteration:
				S.pop()
				p = parent[v]
				if(p):
					low[p] = min(low[p], low[v])

		v = d
		while parent[v] != s:
				if(low[v] >= depth[parent[v]]):
					cut_points.add(parent[v])
				v = parent[v]

		return cut_points
		



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
			moves = state.moves()
			while(True):
				move = random.choice(moves)
				state.play(move)
				moves.remove(move)
				if(state.winner() != gamestate.PLAYERS["none"]):
					last = move
					break

		if(last):
			G = self.get_graph(state, state.winner())
			new_crits = self.find_crit(G, gamestate.EDGE1, gamestate.EDGE2)
			crit_count = len(new_crits)
			self.crit_pts|=new_crits

		return state.winner()

