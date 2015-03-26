# move.py
# handles movement in the world

def toRoom(server, player, command):
	'''
	moves player from their currentRoom to newRoom
	'''
	newRoom = None
	#print "cmd:" + str(command)
	#print "cmd0:" + str(command[0])
	#print str(player.currentRoom.orderedExits)
	# args = <some int>
	if int(command[0]) <= len(player.currentRoom.orderedExits):
		#print player.currentRoom.orderedExits
		#print player.currentRoom.orderedExits[int(command[0])-1]
		targetRoom = player.currentRoom.orderedExits[int(command[0])-1][0]
		#print "tg:" + str(targetRoom)
		for room in server.structureManager.masterRooms:
			#print room.name, room.exits
			if room.ID == targetRoom:
				#print room.ID, room.exits
				newRoom = room
		#print 'nr:' + str(newRoom) + str(newRoom.exits)

	elif int(command[0]) > len(player.currentRoom.orderedExits):
		player.connection.send_cc("^! There are only " + str(len(player.currentRoom.orderedExits)) + " exits!^~\n")
		return


	# args = <exit description text>
	cmdStr = " ".join(command)
	#print "cmdStr:" + cmdStr
	for exit in player.currentRoom.orderedExits:
		if cmdStr == exit[1]:
			newRoom = exit[0]

	if newRoom != None:
		#print player.currentRoom.players
		player.currentRoom.players.remove(player)
		#print player.currentRoom.players
		#print player
		for plyr in player.currentRoom.players:
			plyr.connection.send_cc(player.name + " left.\n")
		for room in server.structureManager.masterRooms:
			if room.ID == newRoom:
				newRoom = room
		player.currentRoom = newRoom
		server.Renderer.roomDisplay(player.connection, player.currentRoom)
		for plyr in player.currentRoom.players:
			plyr.connection.send_cc(player.name + " entered.\n")
		player.currentRoom.players.append(player)

	else:
	# args does not point to an exit
		player.connection.send_cc("^!I am not sure where I want to go!^~\n")
