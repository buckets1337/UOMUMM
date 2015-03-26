#Engine.py
#defines the class representing the game engine

import os, sys
sys.path.append('../')
from passlib.hash import sha256_crypt

import CONFIG
from commands import chat, who, quit, move

class Engine():
	'''
	the engine processes all incoming input from players in real time
	'''
	def __init__(self, owner, server_run, god_list, connected_clients, player_data):
		self.owner = owner
		self.msg = ''
		self.lmsg = ''
		self.cmd = ''
		self.args = ''
		self.player_data_ID = ''
		self.commandSuccess = False
		self.needs_pw = False


	def processClients(self, server_run, god_list, connected_clients, player_data):
		'''
		handles input from clients each tick
		'''
		for client in connected_clients:

			player = player_data[str(client.addrport())]

			self.commandSuccess = self.convertInput(client, player)

			if self.commandSuccess:
				self.needs_pw = self.checkForNewLogin(player)
				if self.needs_pw:
					if player.isFirstTime:
						self.passwordPrompt(client, player)
					else:
						
						#player.loadFromFile()
						self.passwordAuth(client, player)
					if player.authSuccess:
						# load player details from file, if they exist
						self.writePlayerPasswordToFile(client, player)
						player.loadFromFile()
						self.owner.printLog(">> %s [%s] authenticated successfully. (%s)" %(player.player_data_ID, player.name, player.currentRoom.ID), self.owner.log_file)
						client.send_cc("Password confirmed.  Enjoy your time in %s!\n\n" %self.owner.name)
						player.saveToFile()
						if player.currentRoom != None:
							self.owner.Renderer.roomDisplay(player.connection, player.currentRoom)
				self.checkForCommand(client, player)

		# save something each frame to file
		self.owner.saveManager.frameSave()

		return 'normal'


	def convertInput(self, client, player):
		'''
		converts the raw input into useful variables (self.cmd and self.args) for the engine
		'''
		if client.cmd_ready:
			self.player_data_ID = player.player_data_ID

			self.msg = str(client.get_command())
			self.lmsg = self.msg.lower()
			if self.msg == '':
				self.cmd = ''
				return False
			else:
				self.cmd = self.lmsg.split()[0]
			self.args = self.msg.split()[1:]

			return True
		else:
			return False


	def checkForNewLogin(self, player):
		'''
		checks to see if a player just logged in.  If so, the player will have None for a name
		returns True if the player is new, else False
		'''

		if player.authSuccess == False:
			if player.name == None:
				player.name = self.msg

			if player.password == None or player.password.startswith("$5$rounds="):
				return True
			else:
				return False
		else:
			return False


	def passwordPrompt(self, client, player):
		'''
		asks for the player to either enter their password, or make one up
		'''
		path = "../data/client/" + self.owner.name + "/" + player.name + "/" + player.name

		if os.path.isfile(path):
			client.send("\nWelcome back, %s!\n" %player.name)
			client.send("Please enter your password.\n>>")
			player.isNew = False
			player.isFirstTime = False

		else:
			client.send("\nHello, %s!\n" % player.name)
			client.send("Choose a password.  It can be anything, just be sure to remember it.  If you lose your password, your character is gone forever!\n>>")

			file_path = path
			dir_path = "../data/client/" + self.owner.name + "/" + player.name + "/"       
			if not os.path.exists(dir_path):
				os.mkdir(dir_path)
			if not os.path.isfile(file_path):
				f = open(file_path, 'w')
				f.close()
			player.isNew = True
			player.isFirstTime = False


	def writePlayerPasswordToFile(self, client, player):
		'''
		saves the player's password to file
		'''
		path = "../data/client/" + self.owner.name + "/" + player.name + "/" + player.name 

		f = open(path, 'r+')

		firstLine = f.readline()
		if firstLine.startswith("$5$rounds="):
			return
		f.close()

		f = open(path, 'w')
		if player.isNew:
			player.isNew = False
			password = str(sha256_crypt.encrypt(self.msg))
			player.password = password
			# f.write(password + "\n")
			# f.write('name=' + str(player.name) +'\n')
			player.saveToFile()
			f.close()


	def passwordAuth(self, client, player):
		'''
		check if the password entered was correct
		'''

		path = "../data/client/" + self.owner.name + "/" + player.name + "/" + player.name 

		f = open(path, 'r+')

		if player.password is None:
			player.password = f.readline()[:-1]

		if len(player.password) > 0:
			player.authSuccess = sha256_crypt.verify(str(self.msg), player.password)

		else:
			player.authSuccess = True
			self.owner.printLog("No password on file for " + str(player.name), self.owner.log_file)

		if not player.authSuccess:
			if player.numTries == CONFIG.LOGIN_ATTEMPTS - 2:
				client.send_cc("One more attempt before you are kicked.\n")
				player.numTries += 1
				player.lastCmd = str(self.msg)
			elif player.numTries > CONFIG.LOGIN_ATTEMPTS - 2:
				player.numTries = 0
				client.send_cc("Too many failed password attempts.  Goodbye.\n")
				self.owner.printLog(">> Kicking " + str(self.player_data_ID) + " (too many failed pw)", self.owner.log_file)
				client.active = False
				player.active = False
			else:
				client.send_cc("Incorrect password.  Please try again.\n")
				player.numTries += 1
				player.lastCmd = str(self.msg)
				player.isFirstTime = False

		elif player.authSuccess:
			self.needs_pw = False
			
		f.close()


	def checkForCommand(self, client, player):
		'''
		checks self.cmd to see if there is a recognized command
		'''
		#print self.cmd.startswith("'")
		if player.authSuccess:
			if self.cmd == 'quit':
				quit.quitCommand(self, client, player)

			elif self.cmd == 'who':
				who.whoCommand(self, client, player)
				
			elif self.cmd == 'say':			# will eventually be modified to only work in the current room
				messageStr = str(player.name) + ":"
				for arg in self.args:
					messageStr += " " + arg
				self.owner.broadcast(messageStr)

			elif self.cmd == 'chat' or self.cmd == 'c':
				chat.chatCommand(self, client, player)
			
			elif self.cmd.startswith("'") or self.cmd.startswith("`"):
				chat.quickChat(self, client, player)

			elif self.cmd == 'move' or self.cmd == 'm':
				move.toRoom(self.owner, player, self.args)

			elif self.cmd in [str(1),str(2),str(3),str(4),str(5),str(6),str(7),str(8),str(9)]:
				sndlist = [str(self.cmd)]
				move.toRoom(self.owner, player, sndlist)
				