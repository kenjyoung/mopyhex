import numpy as np
from unionfind import unionfind

class gamestate:
	PLAYERS = {"none" : 0, "white" : 1, "black" : 2}
	#represent edges in the union find strucure for win detection
	EDGE1 = 1
	EDGE2 = 2
	def __init__(self, size):
		"""
		Initialize the game board and give white first turn.
		Also create our union find structures for win checking.
		"""
		self.size = size
		self.toplay = self.PLAYERS["white"]
		self.board = np.zeros((size, size))
		self.white_groups = unionfind()
		self.black_groups = unionfind()

	def play(self, cell):
		"""
		Play a stone of the current turns color in the passed cell.
		"""
		if(self.toplay == self.PLAYERS["white"]):
			self.place_white(cell)
			self.toplay = self.PLAYERS["black"]
		elif(self.toplay == self.PLAYERS["black"]):
			self.place_black(cell)
			self.toplay = self.PLAYERS["white"]

	def place_white(self, cell):
		"""
		Place a white stone regardless of whose turn it is.
		"""
		self.board[cell] = self.PLAYERS["white"]
		#if the placed cell touches a white edge connect it appropriately
		if(cell[0] == 0):
			self.white_groups.join(self.EDGE1, cell)
		if(cell[0] == self.size -1):
			self.white_groups.join(self.EDGE2, cell)
		#join any groups connected by the new white stone
		for n in self.neighbors(cell):
			if(self.board[n] == self.PLAYERS["white"]):
				self.white_groups.join(n, cell)

	def place_black(self, cell):
		"""
		Place a black stone regardless of whose turn it is.
		"""
		self.board[cell] = self.PLAYERS["black"]
		#if the placed cell touches a black edge connect it appropriately
		if(cell[1] == 0):
			self.black_groups.join(self.EDGE1, cell)
		if(cell[1] == self.size -1):
			self.black_groups.join(self.EDGE2, cell)
		#join any groups connected by the new black stone
		for n in self.neighbors(cell):
			if(self.board[n] == self.PLAYERS["black"]):
				self.black_groups.join(n, cell)

	def winner(self):
		"""
		Return a number corresponding to the winning player,
		or none if the game is not over.
		"""
		if(self.white_groups.connected(self.EDGE1, self.EDGE2)):
			return self.PLAYERS["white"]
		elif(self.black_groups.connected(self.EDGE1, self.EDGE2)):
			return self.PLAYERS["black"]
		else:
			return self.PLAYERS["none"]


	def neighbors(self, cell):
		"""
		Return list of neighbors of the passed cell.
		"""
		x = cell[0]
		y=cell[1]
		return [(nx , ny) for nx in range(x-1,x+2) for ny in range(y-1, y+2)\
				if (0<=nx and nx<self.size and 0<=ny and ny<self.size and (nx-x)!=(ny-y))]


	def __str__(self):
		"""
		Print an ascii representation of the game board.
		"""
		white = 'O'
		black = '@'
		empty = '.'
		ret = ''
		coord_size = len(str(self.size))
		offset = 1
		ret+=' '*(offset+1)
		for x in range(self.size):
			ret+=chr(ord('A')+x)+' '*offset*2
		ret+='\n'
		for y in range(self.size):
			ret+=str(y+1)+' '*(offset*2+coord_size-len(str(y+1)))
			for x in range(self.size):
				if(self.board[x, y] == self.PLAYERS["white"]):
					ret+=white
				elif(self.board[x,y] == self.PLAYERS["black"]):
					ret+=black
				else:
					ret+=empty
				ret+=' '*offset*2
			ret+=white+"\n"+' '*offset*(y+1)
		ret+=' '*(offset*2+1)+(black+' '*offset*2)*self.size

		return ret