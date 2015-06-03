from gtpinterface import gtpinterface
from gamestate import gamestate
def tournament(interface1, interface2, game_number=100, movetime=10, size=8):
	interface1.send_command("set_time "+str(movetime))
	interface2.send_command("set_time "+str(movetime))
	interface1.send_command("boardsize "+str(size))
	interface2.send_command("boardsize "+str(size))

	win_count = 0
	for i in range(game_number):
		interface1.send_command("clear_board")
		interface2.send_command("clear_board")
		if i%2 == 0:
			while(interface1.send_command("winner")[1] == "none"):
				interface2.send_command("play w "+interface1.send_command("genmove")[1])
				interface1.send_command("play b "+interface2.send_command("genmove")[1])
			if(interface1.send_command("winner")[1] == "white"):
				print("Game complete, winner: agent1(white)")
				win_count+=1
			else:
				print("Game complete, winner: agent2(black)")
				print(interface1.send_command("winner")[1])

		else:
			while(interface1.send_command("winner")[1] == "none"):
				interface1.send_command("play w "+interface2.send_command("genmove")[1])
				interface2.send_command("play b "+interface1.send_command("genmove")[1])
			if(interface1.send_command("winner")[1] == "black"):
				print("Game complete, winner: agent1(black)")
				win_count+=1
			else:
				print("Game complete, winner: agent2(white)")
				print(interface1.send_command("winner")[1])
	return win_count/game_number
