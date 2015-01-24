# Structures.py
# defines world structure objects that form areas and rooms

import os

class StructureManager():
	'''
	handles saving and loading structures
	'''
	def __init__(self, owner):
		self.owner = owner
		self.masterRooms = []	# a list of all room objects in the world
		self.masterAreas = {}	# a dictionary of all areas in the world, with the key being the area ID and the value being the area name


	def createRoom(self, roomData, ownerArea):
		'''
		creates and returns a room object based on the information in roomData file
		'''
		lines = roomData.readlines()

		name = None
		ID = None
		area = None
		description = None
		Long = None
		exits = {}
		orderedExits = []

		for line in lines:
			if line.startswith("name="):
				name = line[5:-1]
			if line.startswith("ID="):
				ID = line[3:-1]
			if line.startswith("description="):
				description = line[12:-1]
			if line.startswith("long="):
				Long = line[5:-1]
			if line.startswith("exits="):
				exitStr = line[6:-1]
				if ", " in exitStr:
					exitList = exitStr.split(", ")
				else:
					exitList = [exitStr]
				print "EXIT:" + str(exitList)
				for exit in exitList:
					exitDesc = exit.split("|")
					#print exitDesc
					# for ext in exitDesc:
					# 	if ext == ['\n']:
					# 		exitDesc.remove(ext)
					print "EL:" + str(exitDesc)
					if exitDesc != ['']:
						exits[exitDesc[0]] = exitDesc[1]
						orderedExits.append(exitDesc)



		if area == None:
			area = ownerArea.ID
		if ID == None or ID == '':
			ID = str(area) + "/" + str(name)


		newRoom = Room(area=area, name=name, ID=ID, exits=exits, description=description, Long=Long)
		newRoom.orderedExits = orderedExits

		self.masterRooms.append(newRoom)
		return newRoom


	def createArea(self, dataFile, path, roomFileList, childAreas):
		'''
		creates and returns an area object based on the information in dataFile and
		the room files contained in path
		'''
		lines = dataFile.readlines()

		name = None
		ID = None
		parent = None
		childList = []
		roomList = []

		for line in lines:
			if line.startswith("name="):
				name = line[5:-1]
			if line.startswith("ID="):
				ID = line[3:-1]


		newArea = Area(parent=parent, children=childList, name=name, ID=ID, rooms=roomList)

		#parent section - get the name of the parent area from the directory tree
		pathlist = path.split("/")
		del pathlist[-1]
		newpath = "/".join(pathlist)
		newArea.parent = newpath

		#child section - get the name of all children areas in a list from the directory tree
		newArea.children = childAreas

		#room section - create a room for each room file located in path, and populate 'roomList'
		for room in roomFileList:
			roomData = open(path+"/"+room)
			newRoom = self.createRoom(roomData, newArea)
			newArea.rooms.append(newRoom)
			roomData.close()


		return newArea





	def loadAreas(self):
		'''
		loads all areas from text files and returns a dictionary 
		where the area name is the key and the area object is the value
		'''
		Areas = {}

		if os.path.exists("../data/world"):
			#print True		#	Load the saved world
			walk = os.walk("../data/world")
			#print str(walk)
			for area in walk:
				#print str(area)
				files = area[2]
				for f in files:
					if f.startswith("_data_"):
						files.remove(f)
						roomFiles = files
						dataFile = open(area[0]+"/"+f)
						Area = self.createArea(dataFile, area[0], roomFiles, area[1])
						Areas[Area.ID] = Area
						dataFile.close()

		else:
			print False		#	Load the blueprint (should be almost the same as above)
			if os.path.exists("../data/blueprint/world"):
				walk = os.walk("../data/blueprint/world")
				print str(walk)

			else:
				self.owner.printLog("No world blueprint present.  Must have top-level 'world' area in 'blueprint' directory in 'data' directory.  World was not loaded.", self.owner.log_file)


		self.masterAreas = Areas

		###########################
		# Startup Console Messages
		###########################
		#print str(self.masterAreas)
		print "\n"
		self.owner.printLog("~* WORLD INFO *~", self.owner.const_log)
		print "\n"
		for area in self.masterAreas:
			if self.masterAreas[area].name != None:
				areaname = str(self.masterAreas[area].name)
			else:
				areaname = 'None'

			self.owner.printLog(areaname + ": room= " + str(self.masterAreas[area].rooms), self.owner.const_log)
			self.owner.printLog((" " * len(areaname)) + "  ID  = " + str(self.masterAreas[area].ID), self.owner.const_log)
			self.owner.printLog((" " * len(areaname)) + "  pare= " + str(self.masterAreas[area].parent), self.owner.const_log)
			self.owner.printLog((" " * len(areaname)) + "  chld= " + str(self.masterAreas[area].children), self.owner.const_log)


			for room in self.masterAreas[area].rooms:
				self.owner.printLog("    " + str(room.name) + "| ID  = " + str(room.ID), self.owner.const_log)
				self.owner.printLog((" " * (len(room.name)+4)) + "| area= " + str(room.area), self.owner.const_log)
				self.owner.printLog((" " * (len(room.name)+4)) + "| desc= " + str(room.description), self.owner.const_log)
				self.owner.printLog((" " * (len(room.name)+4)) + "| Long= " + str(room.Long), self.owner.const_log)
				self.owner.printLog((" " * (len(room.name)+4)) + "| exit= " + str(room.exits), self.owner.const_log)

			self.owner.printLog("\n", self.owner.const_log)







class Area():
	'''
	defined by _data_ files in an area folder.  Intended to be a nested tree of areas, with 'world' at the top
	and the only area that has no parent area
	'''

	def __init__(self, parent, children, name, ID, rooms):
		self.parent = parent
		self.children = children
		self.name = name
		self.ID = ID
		self.rooms = rooms


	def save(self):
		'''
		saves all of the area data to a text file
		'''
		pass


	def load(self):
		'''
		loads the area from a text file
		'''


class Room():
	'''
	Contains information about the spaces the player is actually in. 
	Only knows about itself and the area it is in, should be unaware of
	other rooms that are not exits
	'''

	def __init__(self, area, name, ID, exits, description, Long):
		self.area = area
		self.name = name
		self.ID = ID

		self.description = description
		self.Long = Long

		self.exits = exits	# a dictionary of strings, with the key as the room ID and the value as the display name
		self.orderedExits = []	# a list with the dictionary entries in self.exits in a definite order, themselves lists where list[0] is the roomID and list[1] is the exit's display text

		self.players = []
		self.mobs = []


	def render(self, player):
		'''
		sends a rendered description of the room to the player
		'''
		pass