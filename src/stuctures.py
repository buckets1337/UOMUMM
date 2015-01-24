# stuctures.py
# defines world structure objects that form areas and rooms

import os

class StructureManager():
	'''
	handles saving and loading structures
	'''
	def __init__(self, owner):
		self.owner = owner


	def loadAreas(self):
		'''
		loads all areas from text files and returns a dictionary 
		where the area name is the key and the area object is the value
		'''
		Areas = {}

		if os.path.exists("../data/world"):
			print True
		else:
			print False

		print 'test'





class Area():
	'''
	defined by _data_ files in an area folder.  Intended to be a nested tree of areas, with 'world' at the top
	and the only area that has no parent area
	'''

	def __init__(self, parent, children, name, rooms):
		self.parent = parent
		self.children = children
		self.name = name
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
		self.exits = exits	# a list of strings equivalent to the ID of a room
		self.description = description
		self.Long = Long


	def render(self, player):
		'''
		sends a rendered description of the room to the player
		'''
		pass