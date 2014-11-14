#Engine.py
#defines the class representing the game engine

import os, sys
sys.path.append('../')
from passlib.hash import sha256_crypt

import CONFIG

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
						#self.passwordAuth(client, player)
					else:
						self.writePlayerPasswordToFile(client, player)
						self.passwordAuth(client, player)
					if player.authSuccess:
						#print "WIN"
						self.owner.printLog(">> %s (%s) authenticated successfully." %(player.player_data_ID, player.name), self.owner.log_file)
						player.saveToFile()
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
		# print player.name
		# print self.msg
		if player.authSuccess == False:
			#player just logged in, and does not yet have a name
			if player.name == None:
				player.name = self.msg
				#print 'name:' + player.name

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
			client.send("Please enter your password.\n")
			player.isNew = False
			player.isFirstTime = False

		else:
			client.send("\nHello, %s!\n" % player.name)
			client.send("Choose a password.  It can be anything, just be sure to remember it.  If you lose your password, your character is gone forever!\n")

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
			#print 'self.msg: ' + str(self.msg)
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
		# print 'pwff:' + str(player.password)
		# print len(player.password)

		if len(player.password) > 0:
			# print self.msg, player.password
			# print player.authSuccess
			player.authSuccess = sha256_crypt.verify(str(self.msg), player.password)
			# print self.msg, player.password
			# print player.authSuccess

		else:
			player.authSuccess = True
			# print 'smsg:' + self.msg
			# print 'pw:' + player.password
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
				#print self.owner.cc
			else:
				client.send_cc("Incorrect password.  Please try again.\n")
				player.numTries += 1
				player.lastCmd = str(self.msg)
				player.isFirstTime = False

		elif player.authSuccess:
			self.needs_pw = False
			# print 'success! ' + str(player.authSuccess)
			# print 'pp: ' + str(player.password)

		#player.password = None
		f.close()


	def checkForCommand(self, client, player):
		'''
		checks self.cmd to see if there is a recognized command
		'''
		if self.cmd == 'quit':
			#self.owner.cc.remove(client)
			self.owner.printLog("-- %s quit." %player.name, self.owner.log_file)
			client.active = False

		elif self.cmd == 'who':
			playerNames = ''
			for player in self.owner.pd:
				playerNames += "| " + self.owner.pd[player].name + ((34-len(self.owner.pd[player].name))*" ") + "|\n"
			client.send_cc(" ____Players Currently Connected____\n|" + (35*" ") + "|\n")
			client.send_cc(playerNames)
			client.send_cc("|___________________________________|\n")

		elif self.cmd == 'say':
			messageStr = str(player.name) + ":"
			for arg in self.args:
				messageStr += " " + arg
			self.owner.broadcast(messageStr)


