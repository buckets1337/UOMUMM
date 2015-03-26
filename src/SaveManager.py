# SaveManager.py
# handles rolling saves of the world

import random
import CONFIG

class SaveManager():
	def __init__(self, owner):
		self.owner = owner
		self.areas = []
		self.players = []
		self.rooms = []
		self.timer = CONFIG.SAVE_DELAY

		#print "oa=" + str(owner.structureManager.masterAreas)
		for area in owner.structureManager.masterAreas:
			self.areas.append(owner.structureManager.masterAreas[area])

			# for room in owner.structureManager.masterAreas[area].rooms:
			# 	self.rooms.append(room)

		#print 'op=' + str(owner.player_data)
		for player in owner.player_data:
			self.players.append(owner.player_data[player])

		for room in owner.structureManager.masterRooms:
			self.rooms.append(room)


	def frameSave(self):
		'''
		saves something in the world, once every so many frames, until all objects have been saved
		'''
		if self.timer < 0:
			saveType = random.randint(0,2)

			if saveType == 0:
				# save an area
				if self.areas != []:
					#print "self.areas=" + str(self.areas)
					selected = random.choice(self.areas)
					selected.save()
					#print self.areas
					self.areas.remove(selected)
					#print "new self.areas=" + str(self.areas)
				else:
					#print "@@" + str(self.owner.structureManager.masterAreas)
					for area in self.owner.structureManager.masterAreas:
						self.areas.append(self.owner.structureManager.masterAreas[area])

			elif saveType == 1:
				# save a player
				if self.players != []:
					#print self.players
					selected = random.choice(self.players)
					if selected.name != None and selected.password != None:
						selected.saveToFile()
					self.players.remove(selected)
				else:
					for player in self.owner.player_data:
						self.players.append(self.owner.player_data[player])

			elif saveType == 2:
				# save a room and it's contents
				if self.rooms != []:
					selected = random.choice(self.rooms)
					selected.save()
					self.rooms.remove(selected)
				
				else:
					for room in self.owner.structureManager.masterRooms:
						self.rooms.append(room)

			self.timer = CONFIG.SAVE_DELAY

		else:
			self.timer -=1