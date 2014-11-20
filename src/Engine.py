#Engine.py
#defines the class representing the game engine

import os, sys
sys.path.append('../')
from passlib.hash import sha256_crypt

import CONFIG
from commands import chat as cChat

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
						self.writePlayerPasswordToFile(client, player)
						self.passwordAuth(client, player)
					if player.authSuccess:
						self.owner.printLog(">> %s (%s) authenticated successfully." %(player.player_data_ID, player.name), self.owner.log_file)
						player.saveToFile()
						client.send_cc("Password confirmed.  Enjoy your time in %s!\n\n" %self.owner.name)
				self.checkForCommand(client, player)

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

		if player.isNew:
			player.isNew = False
			f.write(str(sha256_crypt.encrypt(self.msg)) + "\n")
			f.write('name=' + str(player.name) +'\n')
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
				self.owner.printLog("-- %s quit." %player.name, self.owner.log_file)
				client.active = False

			elif self.cmd == 'who':
				playerNames = ''
				for player in self.owner.pd:
					playerNames += self.owner.pd[player].name + '\n'
				self.owner.Renderer.messageBox(client, 'Currently Connected Players', playerNames)
				
			elif self.cmd == 'say':
				messageStr = str(player.name) + ":"
				for arg in self.args:
					messageStr += " " + arg
				self.owner.broadcast(messageStr)

			elif self.cmd == 'chat' or self.cmd == 'c':
				if self.args[0] == 'newChat' or self.args[0] == '/new':		
					if len(self.args) >= 2:
						channelName = ''
						for arg in self.args[1:]:
							channelName += " " + arg
						channelName = channelName[1:]
						cChat.newChannel(self.owner, channelName, player)
					else:
						player.connection.send_cc("What did you want to call the channel?\n")

				elif self.args[0] == 'listChat' or self.args[0] == '/list':
					cChat.listChannels(self.owner, player)

				elif self.args[0] == 'switchChat' or self.args[0] == '/switch':
					if len(self.args) >= 2:
						#print self.args
						channelName = ''
						for arg in self.args[1:]:
							channelName += " " + arg
						channelName = channelName[1:]
						cChat.changeActiveChannel(self.owner, player, channelName)
					else:
						player.connection.send_cc("^!What channel did you want to switch to?^~\n")

				elif self.args[0] == 'leaveChat' or self.args[0] == '/leave':
					if len(self.args) >= 2:
						channelName = ''
						for arg in self.args[1:]:
							channelName += " " + arg
						channelName = channelName[1:]
						cChat.leaveChannel(self.owner, player, channelName)
					else:
						player.connection.send_cc("What channel did you want to leave?\n")

				elif self.args[0] == 'delChat' or self.args[0] == '/del':	# not implemented
					if len(self.args) <= 1:
						if player.activeChatChannel != None:
							cChat.delChannel(self.owner, player.activeChatChannel, player)
						else:
							player.connection.send_cc("^!You must be active in a channel to delete it.\n^~")
					else:
						chanName = ''
						for arg in self.args[1:]:
							chanName += ' ' + arg
						chanName = chanName [1:]
						target = None
						for chan in self.owner.chatManager.chatList:
							if chan.name == chanName:
								target = chan
						if target != None:
							cChat.delChannel(self.owner, target, player)
						else:
							player.connection.send_cc("^!There doesn't appear to be a '" + chanName + "' channel.^~\n")

				elif self.args[0] == 'meChat' or self.args[0] == '/me':		# not implemented
					cChat.playerChannelInfo(self.owner, player)

				elif self.args[0] == 'infoChat' or self.args[0] == '/info':
					if player.activeChatChannel != None:
						player.activeChatChannel.info(player)
					else:
						player.connection.send_cc("^!You must be active in a channel to get information about it.\n^~")

				elif self.args[0] == 'whoChat' or self.args[0] == '/who':
					if player.activeChatChannel != None:
						player.activeChatChannel.listPlayers(player)
					else:
						player.connection.send_cc("^!You must be active in a channel to see who is in it.\n^~")

				elif self.args[0] == 'exitChat' or self.args[0] == '/exit':
					if player.activeChatChannel != None:
						player.activeChatChannel.removePlayer(player)
					else:
						player.connection.send_cc("^!You must be active in a channel to exit it.\n^~")

				else:
					if player.activeChatChannel != None:
						player.activeChatChannel.sendMessage(self.owner, player, self.cmd, self.msg)
					else:
						player.connection.send_cc("^!You are not active in a chat channel!^~\nSwitch to a chat channel to chat.\n")


			elif self.cmd.startswith("'") or self.cmd.startswith("`"):
				targetName = self.cmd[1:]
				if targetName.startswith(' '):
					targetName = targetName[1:]
				if len(targetName) == 0:
					targetName = player.activeChatChannel.name
				msg = ''
				for arg in self.args:
					msg += " " + arg
				msg = msg[1:]
				success = False
				for chan in self.owner.chatManager.chatList:
					if chan.name == targetName:
						if player in chan.players:
							chan.sendMessage(self.owner, player, self.cmd, msg)
							success = True
						else:
							player.connection.send_cc("^!You aren't currently in <" + targetName + ">!^~\nSwitch to <" + targetName + "> to send a message.\n")
							success = True
				if success == False:
					player.connection.send_cc("^!There doesn't appear to be a '" + targetName + "' chat channel.^`\n")
