# Structures.py
# defines world structure objects that form areas and rooms

import os, errno
import CONFIG

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
				#print "EXIT:" + str(exitList)
				for exit in exitList:
					exitDesc = exit.split("|")
					#print exitDesc
					# for ext in exitDesc:
					# 	if ext == ['\n']:
					# 		exitDesc.remove(ext)
					#print "EL:" + str(exitDesc)
					if exitDesc != ['']:
						exits[exitDesc[0]] = exitDesc[1]
						orderedExits.append(exitDesc)



		if area == None:
			area = ownerArea.ID
		if ID == None or ID == '':
			ID = str(area) + "/" + str(name)


		newRoom = Room(owner=self, area=area, name=name, ID=ID, exits=exits, description=description, Long=Long)
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

		if ID == None:
			ID = name


		newArea = Area(owner=self, parent=parent, children=childList, name=name, ID=ID, rooms=roomList)

		#parent section - get the name of the parent area from the directory tree
		pathlist = path.split("/")
		newArea.parentID = pathlist[-2]
		#print pathlist
		del pathlist[-1]
		#print pathlist
		newpath = "/".join(pathlist)
		#print newpath
		newArea.parent = newpath
		#print 'parent=' + str(newArea.parent)
		#print newArea.parentID

		# print "areaPathLabel=" + str(pathlist[-1])
		# print str(pathlist[-1])
		# print self.owner.structureManager.masterAreas
		# for area in self.owner.structureManager.masterAreas:
		# 	print area
		# 	if area == str(pathlist[-1]):
		# 		newArea.parentObject = self.owner.structureManager.masterAreas[area]


		#child section - get the name of all children areas in a list from the directory tree
		newArea.children = childAreas

		#room section - create a room for each room file located in path, and populate 'roomList'
		for room in roomFileList:
			roomData = open(path+"/"+room)
			newRoom = self.createRoom(roomData, newArea)
			newArea.rooms.append(newRoom)
			roomData.close()


		# newArea.path = newArea.getOwnPath()

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
						print 'loading area: ' + str(Area.parent)
						Areas[Area.ID] = Area
						dataFile.close()

		else:
			print "no world data present.  Loading world from blueprints."		#	Load the blueprint (should be almost the same as above)
			if os.path.exists("../data/blueprint/world"):
				walk = os.walk("../data/blueprint/world")
				#print str(walk)
				for area in walk:
				#print str(area)
					files = area[2]
					for f in files:
						if f.startswith("_data_"):
							files.remove(f)
							roomFiles = files
							dataFile = open(area[0]+"/"+f)
							# pathList = area[0].split("/")
							# for path in pathList:
							# 	if path == 'blueprint':
							# 		pathList.remove(path)
							# newPath = "/".join(pathList)
							newPath = area[0]

							Area = self.createArea(dataFile, newPath, roomFiles, area[1])
							print 'loading area: ' + str(Area.parent)
							pathList = area[0].split("/")
							for path in pathList:
								if path == 'blueprint':
									pathList.remove(path)
							Area.parentID = pathList[-1]
							del pathList[-1]
							Area.parent = "/".join(pathList)
							Area.path = "/_data_" + Area.ID
							#print 'ap ' + str(Area.parent) + ' ' + str(Area.parentID) + ' ' + str(Area.path) + ' ' + str(Area.ID)
							Areas[Area.ID] = Area
							dataFile.close()

			else:
				self.owner.printLog("No world blueprint present.  Must have top-level 'world' area in 'blueprint' directory in 'data' directory.  World was not loaded.", self.owner.log_file)



		self.owner.masterAreas = Areas
		self.masterAreas = self.owner.masterAreas

		for area in self.masterAreas:
			#print self.masterAreas[area].path
			self.masterAreas[area].getOwnPath()
			#print self.masterAreas[area].path

			for room in self.masterAreas[area].rooms:
				room.getOwnPath()

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
			self.owner.printLog((" " * len(areaname)) + "  pID = " + str(self.masterAreas[area].parentID), self.owner.const_log)
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

	def __init__(self, owner, parent, children, name, ID, rooms):
		self.owner = owner
		self.parent = parent
		self.parentID = parent
		self.parentObject = None
		self.children = children
		self.name = name
		self.ID = ID
		self.rooms = rooms
		self.path = None



	def getOwnPath(self):
		'''
		walks up the tree and saves the areas found to self.path for filesaving later
		'''
		path = "_data_" + self.ID
		path = self.parent + '/' + self.ID + '/' + path
		self.path = path


		for area in self.owner.masterAreas:
			if self.owner.masterAreas[area].ID == self.parentID:
				self.parentObject = area
				#print 'po=' + str(self.parentObject)



	def save(self):
		'''
		saves all of the area data to a text file
		'''
		# for area in self.owner.masterAreas:
		# 	print self.owner.masterAreas[area].path
		#print self.path
		# if self.path != "world":
		# 	path = self.path + '/' + self.ID
		# else:
		# 	path = "../data/world"

		try:
			os.makedirs(self.parent)
		except OSError as exc: # Python >2.5
			if exc.errno == errno.EEXIST and os.path.isdir(self.parent):
				pass
			else: raise
		try:
			pathList = self.parent.split("/")
			#del pathList[-1]
			newPath = "/".join(pathList) + "/" + self.ID + "/_data_" +self.ID
			anotherPath = newPath.split("/")
			#print anotherPath
			del anotherPath[-1]
			anotherPath = "/".join(anotherPath)
			#print 'ap= ' + str(anotherPath)
			os.makedirs(anotherPath)
			f = open(newPath, 'w')
			f.close()
		except OSError as exc: # Python >2.5
			if exc.errno == errno.EEXIST and (os.path.isfile(newPath) or os.path.isdir(anotherPath)):
				pass
			else: raise
		filename = self.path
		#print filename
		f = open(filename, 'w')

		f.write(str(self) + "\n")
		f.write("name=" + self.name + "\n")
		f.write("ID=" + self.ID + "\n")

		if CONFIG.SAVE_MESSAGES == 'on':
			print "saved area: " + self.ID
		f.close()


	def load(self):
		'''
		loads the area from a text file
		'''
		pass


class Room():
	'''
	Contains information about the spaces the player is actually in. 
	Only knows about itself and the area it is in, should be unaware of
	other rooms that are not exits
	'''

	def __init__(self, owner, area, name, ID, exits, description, Long):
		self.owner = owner
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


	def getOwnPath(self):
		'''
		sets self.path to the proper path for the file that was loaded
		'''
		target = self.owner.masterAreas[self.area]
		areaPath = self.owner.masterAreas[self.area].path

		prePath = areaPath.split("/")
		prePath = prePath[:-2]
		prePath = "/".join(prePath)
		self.path = prePath + "/" + self.ID


	def save(self):
		'''
		saves the room and the objects in the room to file
		'''

		filename = self.path
		#print filename
		pathlist = self.path.split("/")
		pathlist = pathlist[:-1]
		location = "/".join(pathlist)
		#print location

		if os.path.isdir(location):
			try:
				f = open(filename, 'w')

				f.write(str(self) + "\n\n")
				f.write("id=" + self.ID + "\n")				
				f.write("name=" + self.name + "\n")

				exitStr = ''
				for exit in self.orderedExits:
					newExit = exit[0] + "|" + exit[1] + ", "
					exitStr += newExit
				exitStr = exitStr[:-2]
				f.write("exits=" + exitStr + "\n\n")

				f.write("description=" + self.description + "\n")
				f.write("long=" + self.Long + "\n")


				if CONFIG.SAVE_MESSAGES == 'on':
					print "saved room: " + self.ID
				f.close()
			except OSError as exc:
				if exc.errno == errno.EEXIST and (os.path.isfile(self.path)):
					pass
				else: raise