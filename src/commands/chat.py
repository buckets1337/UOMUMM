# chat.py
# subcommands for the 'chat' command relating to more than one channel


def chatCommand(engine, client, player):
	'''
	processes the subcommands of chat
	'''
	if len(engine.args) > 0:
		if engine.args[0] == 'newChat' or engine.args[0] == '/new':						#newChat /new	
			if len(engine.args) >= 2:
				channelName = ''
				for arg in engine.args[1:]:
					channelName += " " + arg
				channelName = channelName[1:]
				newChannel(engine.owner, channelName, player)
			else:
				player.connection.send_cc("What did you want to call the channel?\n")

		elif engine.args[0] == 'listChat' or engine.args[0] == '/list':					#listChat /list
			listChannels(engine.owner, player)

		elif engine.args[0] == 'switchChat' or engine.args[0] == '/switch':				#switchChat /switch
			if len(engine.args) >= 2:
				#print engine.args
				channelName = ''
				for arg in engine.args[1:]:
					channelName += " " + arg
				channelName = channelName[1:]
				changeActiveChannel(engine.owner, player, channelName)
			else:
				player.connection.send_cc("^!What channel did you want to switch to?^~\n")

		elif engine.args[0] == 'leaveChat' or engine.args[0] == '/leave':				#leaveChat /leave
			if len(engine.args) >= 2:
				channelName = ''
				for arg in engine.args[1:]:
					channelName += " " + arg
				channelName = channelName[1:]
				leaveChannel(engine.owner, player, channelName)
			else:
				player.connection.send_cc("What channel did you want to leave?\n")

		elif engine.args[0] == 'delChat' or engine.args[0] == '/del':					#delChat /del
			if len(engine.args) <= 1:
				if player.activeChatChannel != None:
					delChannel(engine.owner, player.activeChatChannel, player)
				else:
					player.connection.send_cc("^!You must be active in a channel to delete it.\n^~")
			else:
				chanName = ''
				for arg in engine.args[1:]:
					chanName += ' ' + arg
				chanName = chanName [1:]
				target = None
				for chan in engine.owner.chatManager.chatList:
					if chan.name == chanName:
						target = chan
				if target != None:
					delChannel(engine.owner, target, player)
				else:
					player.connection.send_cc("^!There doesn't appear to be a '" + chanName + "' channel.^~\n")

		elif engine.args[0] == 'meChat' or engine.args[0] == '/me':						#meChat /me
			playerChannelInfo(engine.owner, player)

		elif engine.args[0] == 'infoChat' or engine.args[0] == '/info':					#infoChat /info
			if player.activeChatChannel != None:
				player.activeChatChannel.info(player)
			else:
				player.connection.send_cc("^!You must be active in a channel to get information about it.\n^~")

		elif engine.args[0] == 'whoChat' or engine.args[0] == '/who':					#whoChat /who
			if player.activeChatChannel != None:
				player.activeChatChannel.listPlayers(player)
			else:
				player.connection.send_cc("^!You must be active in a channel to see who is in it.\n^~")

		elif engine.args[0] == 'exitChat' or engine.args[0] == '/exit':					#exitChat /exit
			if player.activeChatChannel != None:
				player.activeChatChannel.removePlayer(player)
			else:
				player.connection.send_cc("^!You must be active in a channel to exit it.\n^~")

		elif engine.args[0] == 'whitelistChat' or engine.args[0] == '/whitelist':		#whitelistChat /whitelist
			if len(engine.args) >= 2:
				if player.activeChatChannel != None:
					if engine.args[1] == 'show':
						player.activeChatChannel.whitelistShow(player)
					elif engine.args[1] == 'add':
						targetName = ''
						for arg in engine.args[2:]:
							targetName += arg + " "
						targetName = targetName[:-1]
						targetName = targetName.strip()
						player.activeChatChannel.whitelistAdd(player, targetName)
					elif engine.args[1] == 'remove':
						targetName = ''
						for arg in engine.args[2:]:
							targetName += arg + " "
						targetName = targetName[:-1]
						targetName = targetName.strip()
						player.activeChatChannel.whitelistRemove(player, targetName)
					elif engine.args[1] == 'clear':
						player.activeChatChannel.whitelistClear(player)
					else:
						player.connection.send_cc("^!What do you want to do with the whitelist?\n^~")
				else:
					player.connection.send_cc("^!You must be active in a channel to see the channel's whitelist.\n^~")
			else:
				player.connection.send_cc("^!What do you want to do with the whitelist?\n^~")

		elif engine.args[0] == 'blacklistChat' or engine.args[0] == '/blacklist':		#blacklistChat /blacklist
			if len(engine.args) >= 2:
				if player.activeChatChannel != None:
					if engine.args[1] == 'show':
						player.activeChatChannel.blacklistShow(player)
					elif engine.args[1] == 'add':
						targetName = ''
						for arg in engine.args[2:]:
							targetName += arg + " "
						targetName = targetName[:-1]
						targetName = targetName.strip()
						player.activeChatChannel.blacklistAdd(player, targetName)
					elif engine.args[1] == 'remove':
						targetName = ''
						for arg in engine.args[2:]:
							targetName += arg + " "
						targetName = targetName[:-1]
						targetName = targetName.strip()
						player.activeChatChannel.blacklistRemove(player, targetName)
					elif engine.args[1] == 'clear':
						player.activeChatChannel.blacklistClear(player)

					else:
						player.connection.send_cc("^!What do you want to do with the blacklist?\n^~")
				else:
					player.connection.send_cc("^!You must be active in a channel to see the channel's blacklist.\n^~")
			else:
				player.connection.send_cc("^!What do you want to do with the blacklist?\n^~")

		else:																			#notInChannel error
			if player.activeChatChannel != None:
				player.activeChatChannel.sendMessage(engine.owner, player, engine.cmd, engine.msg)
			else:
				player.connection.send_cc("^!You are not active in a chat channel!^~\nSwitch to a chat channel to chat.\n")
	else:
		player.connection.send_cc("^!You have a general idea...but what did you want to do, really?\n")

def quickChat(engine, client, player):
	targetName = engine.cmd[1:]
	if targetName.startswith(' '):
		targetName = targetName[1:]
	if len(targetName) == 0:
		targetName = player.activeChatChannel.name
	msg = ''
	for arg in engine.args:
		msg += " " + arg
	msg = msg[1:]
	success = False
	for chan in engine.owner.chatManager.chatList:
		if chan.name == targetName:
			if player in chan.players:
				chan.sendMessage(engine.owner, player, engine.cmd, msg)
				success = True
			else:
				player.connection.send_cc("^!You aren't currently in <" + targetName + ">!^~\nSwitch to <" + targetName + "> to send a message.\n")
				success = True
	if success == False:
		player.connection.send_cc("^!There doesn't appear to be a '" + targetName + "' chat channel.^`\n")


def newChannel(server, channelName, author):
	'''
	creates a new channel, asking for an optional password
	'''
	newChannel = server.chatManager.createChannel(channelName, author)

	author.connection.send_cc("^!You have created the <%s> chat channel.^~\n" %channelName)


def listChannels(server, player):
	'''
	lists all of the channels that are not password protected
	'''
	channelList = server.chatManager.chatList
	formList = ''
	for chan in channelList:
		mod = ''
		if len(chan.whitelist) != 0:
			mod = " *I* "
		formList += "(" + str(len(chan.players)) + ")" + mod + chan.name + "\n"

	server.Renderer.messageBox(player.connection, 'Public Chat Channels', formList)


def changeActiveChannel(server, player, newChannel):	# should partially migrate to 'addPlayer' on the channel
	'''
	switches to another channel as a target for new input, without leaving the old channel
	'''
	switchTo = None
	for channel in server.chatManager.chatList:
		if channel.name == newChannel:
			switchTo = channel
	if switchTo != None:
		if player not in switchTo.players:
			switchTo.addPlayer(player)
		else:
			switchTo.addPlayer(player, switch = True)

		msg = "   " + player.name + " joined the channel."
		switchTo.printChatLog(msg, msg, printEntry = False)

	else:
		player.connection.send_cc("^!There is not a '" + newChannel + "' channel currently.^~\n")


def leaveChannel(server, player, channel):
	'''
	removes a player from a channel that is not currently active
	'''
	target = None

	for chan in server.chatManager.chatList:
		if chan.name == channel:
			target = chan

	if target != None:
		target.removePlayer(player)
		msg = "   " + player.name + " left the channel."
		target.printChatLog(msg, msg, printEntry = False)
	else:
		player.connection.send_cc("^!You are not connected to a '" + channel + "' channel.^~\n")


def delChannel(server, channel, plyr):	
	'''									
	deletes a chat channel
	'''
	if plyr == channel.author:
		for player in channel.players:
			if player != plyr:
				player.connection.send_cc("^!" + plyr.name + " deleted <" + channel.name +">.\n")
		deleted = None
		deleted = server.chatManager.removeChannel(channel)
		if deleted != None:
			plyr.connection.send_cc("^!You deleted the '" + channel.name + "' chat channel.^~\n")
	else:
		plyr.connection.send_cc("^!You must be the creator of a channel to delete it.^~\n")




def playerChannelInfo(server, player):
	'''
	displays info about the player's current active chat,
	and all chats the player has authored.
	'''
	title = player.name
	if player.activeChatChannel != None:
		active = "Active Channel: (" + str(len(player.activeChatChannel.players)) + ") " + player.activeChatChannel.name + "\n"
	else:
		active = "Active Channel: None\n"
	member = ''
	for chan in player.chatChannels:
		if chan != player.activeChatChannel:
			line = "  (" + str(len(chan.players)) + ") " + chan.name + "\n"
			member += line
		else:
			line = "* (" + str(len(chan.players)) + ") " + chan.name + " *\n"
			member += line
	author = ''
	#print "pn:" + player.name
	for chan in server.chatManager.chatList:
		#print chan.author.name
		if chan.author.name == player.name:
			author += "  (" + str(len(chan.players)) + ") " + chan.name + "\n"

	msg = active + "\n" + "Chats You Are In:\n" + member + "\n" + "Chats You Created:\n" + author
	server.Renderer.messageBox(player.connection, title, msg)