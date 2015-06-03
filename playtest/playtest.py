import sys
sys.path.append("../")
from tournament import tournament
from mctsagent import mctsagent
from gtpinterface import gtpinterface
def main():
	"""
	Run a tournament between two agents and print the resulting winrate
	for the first agent.
	"""
	interface1 = gtpinterface(mctsagent())
	interface2 = gtpinterface(mctsagent())
	print(str(tournament(interface1, interface2, 4, 2, 3)))
	

if __name__ == "__main__":
	main()
