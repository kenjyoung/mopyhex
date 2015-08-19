from gamestate import *
from copy import deepcopy
import random

class miai_gamestate(gamestate):
	"""
	Gamestate that additionally tracks miai connections.
	"""
	#Association between the offset to a potentially miai connected cell
	#and the two cells forming the potential miai connection
	miai_patterns = (((-1,-1) , ((-1, 0),( 0,-1))),
					((-2, 1) , ((-1, 0),(-1, 1))), 
					((-1, 2) , ((-1, 1),( 0, 1))),
					(( 1, 1) , (( 1, 0),( 0, 1))),
					(( 2,-1) , (( 1, 0),( 1,-1))),
					(( 1,-2) , (( 1,-1),( 0,-1))))

	def __init__(self, state):
		self.size = state.size
		self.toplay = state.toplay
		self.board = deepcopy(state.board)
		self.white_groups = deepcopy(state.white_groups)
		self.black_groups = deepcopy(state.black_groups)
		self.white_pairs = {}
		self.black_pairs = {}
		self.compute_miais()
		self.lastmove = None

	def recompute_groups(self):
		#clear groups and recompute all (nonvirtual) connections on the board
		self.white_groups = unionfind()
		self.black_groups = unionfind()
		for i in range(self.size):
			for j in range(self.size):
				cell = (i,j)
				if self.board[cell]==self.PLAYERS["none"]: continue

				if self.board[cell]==self.PLAYERS["white"]:
					#if the placed cell touches a white edge connect it appropriately
					if(cell[0] == 0):
						self.white_groups.join(self.EDGE1, cell)
					if(cell[0] == self.size -1):
						self.white_groups.join(self.EDGE2, cell)
					for n in self.neighbors(cell):
						if(self.board[n] == self.PLAYERS["white"]):
							self.white_groups.join(cell, n)
				elif self.board[cell]==self.PLAYERS["black"]:
					#if the placed cell touches a black edge connect it appropriately
					if(cell[1] == 0):
						self.black_groups.join(self.EDGE1, cell)
					if(cell[1] == self.size -1):
						self.black_groups.join(self.EDGE2, cell)
					for n in self.neighbors(cell):
						if(self.board[n] == self.PLAYERS["black"]):
							self.black_groups.join(cell, n)
				else:
					raise ValueError("Unrecognized player")


	def compute_miais(self):
		#update miai connections for every cell on the board
		#in random order to avoid bias
		self.black_pairs = {}
		self.white_pairs = {}
		shuffled_i = list(range(self.size))
		shuffled_j = list(range(self.size))
		random.shuffle(shuffled_i)
		random.shuffle(shuffled_j)
		for i in shuffled_i:
			for j in shuffled_j:
				if(self.board[i,j]!=self.PLAYERS["none"]):
					self.update_miais((i,j))

	def update_miais(self, cell):
		player = self.board[cell]
		if player == self.PLAYERS["white"]:
			pairs = self.white_pairs
			groups = self.white_groups
		elif player == self.PLAYERS["black"]:
			pairs = self.black_pairs
			groups = self.black_groups
		else:
			raise ValueError("Unknown Player")

		#shuffle the miai patterns so we check in random order to avoid bias
		#in case of conflict
		shuffled_miai_patterns = list(self.miai_patterns)
		random.shuffle(shuffled_miai_patterns)
		for p in shuffled_miai_patterns:
			c =  (p[0][0]   +cell[0], p[0][1]   +cell[1])  #potential connection
			m = ((p[1][0][0]+cell[0], p[1][0][1]+cell[1]), 
				 (p[1][1][0]+cell[0], p[1][1][1]+cell[1])) #associated miai pair

			#if the potential connection is out of bounds need only check for miai
			#connections with player owned edges
			if(c[0]<0 or c[0]>self.size-1 or c[1]<0 or c[1]>self.size-1):
				#if any of the cells in the miai pair are also out of bounds
				#there can be no miai connection to an edge
				if(m[0][0]<0 or m[0][0]>self.size-1 or m[0][1]<0 or m[0][1]>self.size-1\
				or m[1][0]<0 or m[1][0]>self.size-1 or m[1][1]<0 or m[1][1]>self.size-1):
					continue

				if(player == self.PLAYERS["white"]):
					if(c[0] == -1):
						c = self.EDGE1
					elif(c[0] == self.size):
						c = self.EDGE2
					else:
						continue

				if(player == self.PLAYERS["black"]):
					if(c[1] == -1):
						c = self.EDGE1
					elif(c[1] == self.size):
						c = self.EDGE2
					else:
						continue


			#if the two cells invloved in the miai pair are not both empty there
			#is no miai connection
			if not(self.board[m[0]] == self.board[m[1]] == self.PLAYERS["none"]):
				continue

			#if we don't own control the potential connected cell there is no
			#miai connection
			if not(c == self.EDGE1 or c == self.EDGE2 or self.board[c] == player):
				continue

			#if either of the two cells in the miai pair is involved in another
			#miai connection, we cannot also involve it in this one
			if m[0] in pairs or m[1] in pairs:
				continue

			#join the newly miai-connected groups
			if groups.join(cell, c):
				#add the associated miai pair to the pairs dictionary
				#unless the groups are already the same in which case this connection
				#is redundant
				self.set_miai(m[0], m[1], player)
				assert(self.board[m[0]]==self.board[m[1]]==0)

	def clear_miai(self, cell, player):
		if player == self.PLAYERS["white"]:
			pairs = self.white_pairs
		elif player == self.PLAYERS["black"]:
			pairs = self.black_pairs
		else:
			raise ValueError("Unknown Player")

		if cell in pairs:
			other = pairs[cell]
			del pairs[cell]
			del pairs[other]

	def set_miai(self, cell1, cell2, player):
		if player == self.PLAYERS["white"]:
			pairs = self.white_pairs
		elif player == self.PLAYERS["black"]:
			pairs = self.black_pairs
		else:
			raise ValueError("Unknown Player")

		pairs[cell1] = cell2
		pairs[cell2] = cell1


	def get_miai(self, cell, player = None):
		if player == None:
			player = self.toplay

		if(player == self.PLAYERS["white"]):
			if cell not in self.white_pairs:
				return None
			else:
				return self.white_pairs[cell]
		elif(player ==self.PLAYERS["black"]):
			if cell not in self.black_pairs:
				return None
			else:
				return self.black_pairs[cell]
		else:
			#unrecognized player
			return None

	def miai_winner(self):
		"""
		Return a number corresponding to the winning player (including wins by
		virtual connection), or none if the game is not over.
		"""
		if(self.white_groups.connected(self.EDGE1, self.EDGE2)):
			return self.PLAYERS["white"]
		elif(self.black_groups.connected(self.EDGE1, self.EDGE2)):
			return self.PLAYERS["black"]
		else:
			return self.PLAYERS["none"]

	def winner(self):
		"""
		Return a number corresponding to the winning player,
		or none if the game is not over (does not count miai connections towards
		win)
		"""
		#for now this just returns the miai winner
		#TODO: implement properly if nessesary
		return self.miai_winner

	def place_white(self, cell):
		"""
		Place a white stone regardless of whose turn it is.
		"""
		if(cell in self.white_pairs):
			self.clear_miai(cell, self.PLAYERS["white"])

		super().place_white(cell)
		#if the last move was part of one of our miai pairs and we don't respond
		#with the other member of the pair, our miai connectivity is invalidated 
		#and must be recomputed
		if(self.lastmove in self.white_pairs):
			if(self.white_pairs[self.lastmove]!=cell):
				self.recompute_groups()
				self.compute_miais()
			else:
				self.clear_miai(self.lastmove, self.PLAYERS["white"])
		else:
			self.update_miais(cell)
		self.lastmove = cell

	def place_black(self, cell):
		"""
		Place a black stone regardless of whose turn it is.
		"""
		#if the cell is a miai connection clear it
		if(cell in self.black_pairs):
			self.clear_miai(cell, self.PLAYERS["black"])

		super().place_black(cell)
		#if the last move was part of one of our miai pairs and we don't respond
		#with the other member of the pair, our miai connectivity is invalidated 
		#and must be recomputed
		if(self.lastmove in self.black_pairs):
			if(self.black_pairs[self.lastmove]!=cell):
				self.recompute_groups()
				self.compute_miais()
			else:
				self.clear_miai(self.lastmove, self.PLAYERS["black"])
		else:
			self.update_miais(cell)
		self.lastmove = cell
