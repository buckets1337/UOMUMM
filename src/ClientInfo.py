#ClientInfo.py
#definition of a class representing one connected client.

import os
import CONFIG

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
		self.currentRoom = None

		self.activeChatChannel = None
		self.chatChannels = []


	def saveToFile(self):
		'''
		saves all data to a text file
		'''
		self.path = "../data/client/" + self.owner.name + "/" + self.name + "/" + self.name
		f = open(self.path, 'w')

		if self.password != None:
			#print 's.pw=' + self.password
			f.write(str(self.password) + "\n")
		else:
			f.write("\n")
		f.write("name=" + self.name + "\n")
		f.write("prompt=" + self.prompt + "\n")

		f.write("gameState=" + self.gameState + "\n")
		if self.currentRoom != None:
			f.write("currentRoom=" + str(self.currentRoom.ID) + "\n")
		if CONFIG.SAVE_MESSAGES == 'on':
			print "saved player:" + self.name


	def loadFromFile(self):
		'''
		loads all data from player's text file
		'''
		self.path = "../data/client/" + self.owner.name + "/" + self.name + "/" + self.name

		if os.path.exists(self.path):
			f = open(self.path, 'r')

			lines = f.readlines()

			#print lines

			if lines != []:
				self.password = lines[0]

			for line in lines:
				if line.startswith("name="):
					self.name = line[5:-1]
				if line.startswith("prompt="):
					self.prompt = line[7:-1]
				if line.startswith("gameState="):
					self.gameState = line[10:-1]
				if line.startswith("currentRoom="):
					currentRoom = line[12:-1]
					print currentRoom
					print self.owner.structureManager.masterRooms
					for room in self.owner.structureManager.masterRooms:
						print room.ID
						if currentRoom == room.ID:
							self.currentRoom = room
							room.players.append(self)
							#print room.players
		#print 'cr:' + str(self.currentRoom)
		if self.currentRoom == None:
			currentRoom = CONFIG.STARTING_ROOM
			for room in self.owner.structureManager.masterRooms:
				if currentRoom == room.ID:
					self.currentRoom = room
					room.players.append(self)
		#print self.currentRoom

