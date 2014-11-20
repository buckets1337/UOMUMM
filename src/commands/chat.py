# cChat.py
# subcommands for the 'chat' command relating to more than one channel



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
		formList += "(" + str(len(chan.players)) + ") " + chan.name + "\n"

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