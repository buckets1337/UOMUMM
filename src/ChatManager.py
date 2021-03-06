# ChatManager.py
# defines the chatManager, which handles chat channels
import time, os

class chatManager():
	'''
	a chatManager handles storing, creating, and deleting chat channels
	'''
	def __init__(self, owner):
		self.chatList = []
		self.owner = owner

	def createChannel(self, channelName, author):	
		'''
		creates a new chat channel and adds it to the chat list
		'''
		newChannel = chatChannel(self, channelName, author)
		newChannel.players.append(author)

		author.activeChatChannel = newChannel
		author.chatChannels.append(newChannel)

		self.chatList.append(newChannel)


	def removeChannel(self, channel, byAuthor = True):
		'''
		deletes a chat channel from the chatList
		'''
		for chan in self.chatList:
			if chan == channel:
				self.chatList.remove(chan)
				for player in chan.players:
					if chan == player.activeChatChannel:
						player.activeChatChannel = None
					player.chatChannels.remove(chan)
				timestamp = time.strftime('%b %d, %Y  %H:%M:%S')
				if byAuthor == True:
					msg = ("-c <" + chan.name + "> Deleted " + timestamp + " by " + chan.author.name)
				else:
					msg = ("-c <" + chan.name + "> Deleted " + timestamp + " by " + byAuthor)
				self.owner.printLog(msg, self.owner.log_file)
				self.owner.printLog(msg, self.owner.chat_log_file_byDate, printEntry = False)
				self.owner.printLog(msg, chan.chat_channel_log, printEntry = False)

				return True


	def broadcast(self, sender, message):
		'''
		sends a message to ALL chat channels
		'''
		for chan in self.chatList:
			chan.sendMessage(self.owner, sender, "   ", message)



class chatChannel():
	'''
	a chatChannel is the keeper of messages for one chat 
	'''
	def __init__(self, owner, channelName, author):
		self.owner = owner
		self.messages = []
		self.players = []
		self.whitelist = []
		self.blacklist = []
		self.name = channelName
		self.author = author
		self.password = None
		self.timestamp = time.strftime('%b %d, %Y  %H:%M:%S')
		self.datestamp = time.strftime('%b_%d_%Y')
		self.shortTimestamp = time.strftime('%H_%M_%S')
		self.chat_channel_log_path = self.owner.owner.chat_log_file_byChannel + self.name +'/'
		self.chat_channel_log =  self.chat_channel_log_path + self.datestamp
		#self.chat_channel_log_file =  self.chat_channel_log + '/' + self.shortTimestamp

		if not os.path.exists(self.chat_channel_log_path):
			os.mkdir(self.chat_channel_log_path)

		# if  not os.path.exists(self.chat_channel_log):
		# 	os.mkdir(self.owner.owner.chat_log_file_byChannel + self.chat_channel_log)

		if not os.path.exists(self.chat_channel_log):
			f = open(self.chat_channel_log, 'a')
			f.close()

		msg = ("+c <" + self.name + "> Created " + self.timestamp + " by " + self.author.name)
		shortMsg = msg
		self.printChatLog(msg, shortMsg)
		# self.owner.owner.printLog(msg, self.owner.owner.log_file)
		# self.owner.owner.printLog(msg, self.owner.owner.chat_log_file_byDate, printEntry = False)
		# self.owner.owner.printLog(msg, self.chat_channel_log, printEntry = False)


	def printChatLog(self, msg, shortMsg, printEntry = True):
		'''
		prints a message to the chat logs and the all log
		'''
		if printEntry:
			self.owner.owner.printLog(msg, self.owner.owner.log_file)
		else:
			self.owner.owner.printLog(msg, self.owner.owner.log_file, printEntry = False)
		self.owner.owner.printLog(msg, self.owner.owner.chat_log_file_byDate, printEntry = False)
		self.owner.owner.printLog(msg, self.chat_channel_log, printEntry = False)


	def addMessage(self, player, message):
		'''
		adds a message entry to self.messages
		'''
		messagesEntry = player.name + ": " + message
		self.messages.append(messagesEntry)


	def sendMessage(self, server, player, commandString, message):
		'''
		sends a message to all players in the channel
		'''
		msg = message.replace(commandString+' ', '')
		entry = "^!<" + self.name + ">^~ ^U" + player.name + "^~: " + msg + "\n"
		logEntry = "   <" + self.name + "> " + player.name + ": " + msg
		shortLogEntry = player.name + ": " + msg
		for plyr in self.players:
			plyr.connection.send_cc(entry)

		self.printChatLog(logEntry, shortLogEntry)

		self.addMessage(player, msg)


	def addPlayer(self, player, switch = False):
		'''
		adds a player to the chat channel, checking the password if one is present
		'''
		addPlayer = False
		if len(self.whitelist) != 0:
			#should only allow a player to join the channel if they are on the whiteList
			if player == self.author or (player.name in self.whitelist):
				addPlayer = True
			else:
				player.connection.send_cc("It appears you are not allowed in this channel.\n")
				
		elif len(self.blacklist) != 0:
			#should only allow a player to join the channel if they are on the blackList
			if player == self.author or (player.name not in self.blacklist):
				addPlayer = True
			else:
				player.connection.send_cc("It appears you are not allowed in this channel.\n")
		else:
			addPlayer = True

		if addPlayer:
			player.activeChatChannel = self
			if player not in self.players:
				self.players.append(player)
				player.chatChannels.append(self)
			if switch == False:
				player.connection.send_cc("^!Welcome to <" + player.activeChatChannel.name + ">.^~\n")
				if str(len(self.players) - 1) > 1:
					player.connection.send_cc(str(len(self.players) - 1) + " other players.\n")
				elif str(len(self.players) - 1) == 1:
					player.connection.send_cc(str(len(self.players) - 1) + " other player.\n")
				else:
					player.connection.send_cc("No other players.\n")
			else:
				if str(len(self.players) - 1) > 1:
					player.connection.send_cc("^!Switched to <" + player.activeChatChannel.name + "> (" + str(len(player.activeChatChannel.players) - 1) + " others).^~\n")
				elif str(len(self.players) - 1) == 1:
					player.connection.send_cc("^!Switched to <" + player.activeChatChannel.name + "> (" + str(len(player.activeChatChannel.players) - 1) + " other).^~\n")
				else:
					player.connection.send_cc("^!Switched to <" + player.activeChatChannel.name + "> (No others).^~\n")

			for plyr in self.players:
				if plyr != player:
					if switch == False:
						msg = "^!<" + self.name + ">^~ " +player.name + " joined the channel.\n"
						plyr.connection.send_cc(msg)

			self.addMessage(player, "joined the channel.")


	def removePlayer(self, player, kicked=False):
		'''
		removes a player from the channel
		'''
		self.players.remove(player)
		player.chatChannels.remove(self)

		if not kicked:
			player.connection.send_cc("^!You have left <" + self.name + ">.^~\n")
		else:
			player.connection.send_cc("^!You were kicked from <" + self.name + ">.^~\n")

		for plyr in self.players:
			if not kicked:
				msg = "^!<" + self.name + ">^~ " +player.name + " left the channel.\n"
			else:
				msg = "^!<" + self.name + ">^~ " + player.name + " was kicked from the channel.\n"
			plyr.connection.send_cc(msg)
		if not kicked:
			self.addMessage(player, "left the channel.")
		else:
			self.addMessage(player, "was kicked.")

		if player.activeChatChannel == self:
			player.activeChatChannel = None

	
	def info(self, player):
		'''
		displays information about the current channel and a list of players connected to the channel
		'''
		formMsg = ''
		formMsg += 'Channel Author: ' + self.author.name + '\n'
		formMsg += 'Created: ' + self.timestamp + '\n\n'
		if self.whitelist != []:
			formMsg += 'whitelist active\n\n'
		if self.blacklist != []:
			formMsg += 'blacklist active\n\n'
		formMsg += 'Players:\n'
		for plyr in self.players:
			formMsg += plyr.name + '\n'

		if len(self.players) == 1:
			mod = ''
		else:
			mod = 's'

		formMsg += '\n(' + str(len(self.players)) + ' connected player' + mod + ')'

		self.owner.owner.Renderer.messageBox(player.connection, self.name, formMsg)


	def listPlayers(self, player):
		'''
		displays a list of all the players currently connected to a channel
		'''
		formMsg = ''
		for plyr in self.players:
			formMsg += plyr.name + '\n'

		if len(self.players) == 1:
			mod = ''
		else:
			mod = 's'

		formMsg += '\n(' + str(len(self.players)) + ' connected player' + mod + ')'

		self.owner.owner.Renderer.messageBox(player.connection, self.name, formMsg)


	def whitelistShow(self, player):
		'''
		shows the whitelist for the chat channel
		'''
		title = "<" + self.name + ">'s Whitelist"
		wlstr = ''
		for playerName in self.whitelist:
			wlstr += playerName + "\n"
		self.owner.owner.Renderer.messageBox(player.connection, title, wlstr)


	def whitelistAdd(self, player, target):
		'''
		if the player issuing the command is the channel's author, add the target player to the whiteList
		'''
		if player == self.author:
			if target not in self.whitelist:
				self.whitelist.append(target)
				player.connection.send_cc("%s was added to the whitelist.\n" %target)
			else:
				player.connection.send_cc("%s is already on the whitelist.\n" %target)
		else:
			player.connection.send_cc("You must be the author of a channel to add players to the whitelist.\n")


	def whitelistRemove(self, player, target):
		'''
		if the player issuing the command is the channel's author, remove the target player from the whiteList
		'''
		if player == self.author:
			if target in self.whitelist:
				self.whitelist.remove(target)
				for plyr in self.players:
					if plyr.name == target:
						self.removePlayer(plyr, kicked=True)
				#print self.whitelist, len(self.whitelist)
				player.connection.send_cc("%s was removed from the whitelist.\n" %target)
			else:
				player.connection.send_cc("%s is not on the whitelist.\n" %target)
		else:
			player.connection.send_cc("You must be the author of a channel to remove players from the whitelist.\n")


	def whitelistClear(self, player):
		'''
		clears the whitelist of all players
		'''
		if player == self.author:
			self.whitelist = []
			player.connection.send_cc("^!<%s>'s whitelist cleared.^~\n" %self.name)

	def blacklistShow(self, player):
		'''
		shows the whitelist for the chat channel
		'''
		title = "<" + self.name + ">'s Blacklist"
		blstr = ''
		for playerName in self.blacklist:
			blstr += playerName + "\n"
		self.owner.owner.Renderer.messageBox(player.connection, title, blstr)


	def blacklistAdd(self, player, target):
		'''
		if the player issuing the command is the channel's author, add the target player to the whiteList
		'''
		if player == self.author:
			if target not in self.blacklist:
				self.blacklist.append(target)
				for plyr in self.players:
					if plyr.name == target:
						self.removePlayer(plyr, kicked=True)
				player.connection.send_cc("%s was added to the blacklist.\n" %target)
			else:
				player.connection.send_cc("%s is already on the blacklist.\n" %target)
		else:
			player.connection.send_cc("You must be the author of a channel to add players to the blacklist.\n")


	def blacklistRemove(self, player, target):
		'''
		if the player issuing the command is the channel's author, remove the target player from the whiteList
		'''
		if player == self.author:
			if target in self.blacklist:
				self.blacklist.remove(target)
				player.connection.send_cc("%s was removed from the blacklist.\n" %target)
			else:
				player.connection.send_cc("%s is not on the blacklist.\n" %target)
		else:
			player.connection.send_cc("You must be the author of a channel to remove players from the blacklist.\n")


	def blacklistClear(self, player):
		'''
		clears the blacklist of all players
		'''
		if player == self.author:
			self.blacklist = []
			player.connection.send_cc("^!<%s>'s blacklist cleared.^~\n" %self.name)