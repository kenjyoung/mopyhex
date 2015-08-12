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
		S.append((s, None))
		visited = set()
		leaves = []
		depth = {}
		dest = {} #does the DFS subtree at each vertex contain dest?
		#root has parent None and depth 0 so...
		depth[None] = -1
		parent = {}
		low = {}

		while S:
			v, p = S.pop()
			if not v in visited:
				visited.add(v)
				parent[v] = p
				depth[v] = depth[p] +1
				low[v] = depth[v]
				leaf = True
				for n in G[v]:
					if n not in visited:
						leaf = False
					elif n is not parent[v]:
						low[v] = min(low[v],low[n])
					S.append((n,v))
				if leaf:
					leaves.append(v)

		#backpropogate info from leaf nodes
		for v in leaves:
			while parent[v]:
				low[parent[v]] =min(low[parent[v]],low[v])
				v = parent[v]

		#and search the ancestors of our destination for separation points
		v = d
		while parent[v]!=s:
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
			while(True):
				moves = state.moves()
				move = random.choice(moves)
				state.play(move)
				moves.remove(move)
				if(state.winner() != gamestate.PLAYERS["none"]):
					last = move
					break

		if(last):
			G = self.get_graph(state, state.winner())
			self.crit_pts|=self.find_crit(G, gamestate.EDGE1, gamestate.EDGE2)

		return state.winner()

