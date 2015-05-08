import numpy as np

class gamestate:
	def __init__(self, size):
		self.size = size
		self.board = np.zeros((size, size))

	def play_white(self, cell):
		self.board[cell] = 1

	def play_black(self, cell):
		self.board[cell] = -1

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
				if(self.board[x, y] == 1):
					ret+=white
				elif(self.board[x,y] == -1):
					ret+=black
				else:
					ret+=empty
				ret+=' '*offset*2
			ret+=white+"\n"+' '*offset*(y+1)
		ret+=' '*(offset*2+1)+(black+' '*offset*2)*self.size

		return ret