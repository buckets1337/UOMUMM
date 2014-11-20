#ClientInfo.py
#definition of a class representing one connected client.

class ClientInfo():
	def __init__(self, owner, name, prompt, client, ID, player_data_ID):
		self.owner = owner
		self.path = None
		self.name = None
		self.password = None
		self.prompt = prompt

		self.connection = client
		self.ID = ID		#connection ID, representing the count of clients to have logged in since server start.
		self.player_data_ID = player_data_ID

		self.isFirstTime = True
		self.isNew = True
		self.authSuccess = False
		self.numTries = 0

		self.active = False		#is the client still connected?
		self.gameState = 'normal'

		self.activeChatChannel = None
		self.chatChannels = []


	def saveToFile(self):
		'''
		saves all data to a text file
		'''
		self.path = "../data/client/" + self.owner.name + "/" + self.name + "/" + self.name
		f = open(self.path, 'w')

		f.write(self.password + "\n")
		f.write("name=" + self.name + "\n")
		f.write("prompt=" + self.prompt + "\n")

		f.write("gameState=" + self.gameState + "\n")

