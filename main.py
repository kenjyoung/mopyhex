from gtpinterface import gtpinterface
from mctsagent import mctsagent
from crit_mctsagent import crit_mctsagent
from ext_crit_mctsagent import ext_crit_mctsagent
def main():
	"""
	Main function, simply sends user input on to the gtp interface and prints
	responses.
	"""
	agent = crit_mctsagent()
	interface = gtpinterface(agent)
	while True:
		command = input()
		success, response = interface.send_command(command)
		print(("= " if success else "? ")+response+'\n')

if __name__ == "__main__":
	main()
