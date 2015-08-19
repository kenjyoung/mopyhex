import sys
sys.path.append("../")
from tournament import tournament
from mctsagent import mctsagent
from crit_mctsagent import crit_mctsagent
from gamestate import gamestate
from gtpinterface import gtpinterface
def main():
	"""
	Run a tournament between two agents and print the resulting winrate
	for the first agent.
	"""
	if len(sys.argv)<3:
		print("Please provide the names of 2 agents to test against each other.")
		return

	interface1 = gtpinterface(sys.argv[1])
	interface2 = gtpinterface(sys.argv[2])
	print("Winrate for agent1 ("+interface1.agent_name+") "+str(tournament(interface1, interface2, 200, 15, 9)))
	

if __name__ == "__main__":
	main()
