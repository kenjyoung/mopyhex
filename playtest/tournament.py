from gtpinterface import gtpinterface
from gamestate import gamestate

def print_game(game):
	for move in game:
		print(move, end=' ')
	print()

def tournament(interface1, interface2, game_number=100, movetime=10, size=8):
	"""
	Run some number of games between two agents, alternating who has first move
	each time. Return the winrate for the first of the two agents.
	"""
	interface1.send_command("set_time "+str(movetime))
	interface2.send_command("set_time "+str(movetime))
	interface1.send_command("boardsize "+str(size))
	interface2.send_command("boardsize "+str(size))

	win_count = 0
	for i in range(game_number):
		game = []
		interface1.send_command("clear_board")
		interface2.send_command("clear_board")
		if i%2 == 0:
			while(interface1.send_command("winner")[1] == "none"):
				move = interface1.send_command("genmove white")
				if move[0]: 
					interface2.send_command("play w "+move[1])
					game.append(move[1])
				move = interface2.send_command("genmove black")
				if move[0]:
					interface1.send_command("play b "+move[1])
					game.append(move[1])

			print_game(game)
			if(interface1.send_command("winner")[1] == "white"):
				print("Game complete, winner: agent1(white)\n")
				win_count+=1
			else:
				print("Game complete, winner: agent2(black)\n")

		else:
			while(interface1.send_command("winner")[1] == "none"):
				move = interface2.send_command("genmove white")
				if move[0]: 
					interface1.send_command("play w "+move[1])
					game.append(move[1])
				move = interface1.send_command("genmove black")
				if move[0]: 
					interface2.send_command("play b "+move[1])
					game.append(move[1])

			print_game(game)	
			if(interface1.send_command("winner")[1] == "black"):
				print("Game complete, winner: agent1(black)\n")
				win_count+=1
			else:
				print("Game complete, winner: agent2(white)\n")

	return win_count/game_number
