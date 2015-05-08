from gtpinterface import gtpinterface
from mctsagent import mctsagent
def main():
	agent = mctsagent
	interface = gtpinterface(agent)
	while True:
		command = input()
		response = interface.send_command(command)
		print(response)

if __name__ == "__main__":
	main()