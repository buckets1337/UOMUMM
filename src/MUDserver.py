#!/usr/bin/env python
#------------------------------------------------------------------------------
#   MUDserver.py
#   
#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain a
#   copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.
#------------------------------------------------------------------------------


# note to myself on naming conventions:
# lowercase and underscore for attributes, ex: self.my_stat
# camelcase for object methods, ex: self.doSomething
# camelcase for local variable, ex: myVariable
# super camelcase for objects, ex: self.MyEngine

"""
Simple MUD server using miniboa
"""
import time, os, sys
import Engine, ClientInfo, Renderer
import CONFIG
sys.path.append('../')
from miniboa import TelnetServer


class Server():
	'''
	The game server object.  Holds all other objects in the game.
	'''
	def __init__(self):
		self.name = str(sys.argv[2])
		self.port = int(sys.argv[1])
		self.id_counter = 0
		self.idle_timeout = CONFIG.IDLE_TIMEOUT
		self.log_file = None
		self.connected_clients = []
		self.cc = self.connected_clients
		self.server_run = True
		self.engine_state = 'running'
		self.player_data = {}
		self.pd = self.player_data
		self.timers = []
		self.move_timers = []
		self.current_time = 0
		self.startup_time = time.time()
		self.delta_time = 0
		self.last_time = 0
		self.god_list = []

		# with open('../data/god_list', 'r') as f:
		# 	self.god_list = f.readlines()

		self.setupLog()
		self.setupClientRecords()

		self.TelnetServer = TelnetServer(
		#address should be a blank string for deployment across a network, as blank allows the server to use any network interface it finds.
		#localhost is for testing where server and clients both exist on one computer, without going across the network
		port=self.port,
		address='localhost',
		on_connect=self.on_connect,
		on_disconnect=self.on_disconnect,
		timeout = .05
		)

		self.Engine = Engine.Engine(self, self.server_run, self.god_list, self.cc, self.pd)
		self.Renderer = Renderer.Renderer(self)
		


	def RUN(self):
		'''
		main loop for the server
		'''

		while self.server_run:

			self.TelnetServer.poll()        ## Send, Recv, and look for new connections

			self.kickIdle()     ## Check for idle clients

			self.current_time = time.time()
			self.delta_time = (self.current_time - self.startup_time) - self.last_time

			for timer in self.timers:
				timer.tick(self.delta_time)
			for timer in self.move_timers:
				timer.tick(self.delta_time)    
			self.last_time = (self.current_time - self.startup_time)

			self.engine_state = self.Engine.processClients(self.server_run, self.god_list, self.cc, self.pd)           ## Check for client input, saving any state changes generated by the engine to 'engineState'

			self.stateCheck()


	def setupLog(self):
		'''
		creates server log files for writing in later
		'''
		time_string = time.strftime('%H_%M_%S')
		date = time.strftime('%m_%d')
		dataPath = '../data/'
		logPath = '../data/log/'
		server_path = '../data/log/' + self.name + '/'
		all_path = '../data/log/' + self.name + '/all/'
		path = '../data/log/' + self.name + '/all/' + date + '/'
		file_path = '../data/log/' + self.name + '/all/' + date + '/' + time_string

		if not os.path.exists(dataPath):
			os.mkdir(dataPath)
		if not os.path.exists(logPath):
			os.mkdir(logPath)
		if not os.path.exists(server_path):
			os.mkdir(server_path)
		if not os.path.exists(all_path):
			os.mkdir(all_path)
		if not os.path.exists(path):
			os.mkdir(path)
		if not os.path.exists(file_path):
			f = open(file_path, 'a')
			f.close()

		self.log_file = file_path


	def setupClientRecords(self):
		'''
		initializes the client records 
		'''
		path = '../data/client/'
		if not os.path.exists(path):
			os.mkdir(path)
		serverPath = '../data/client/' + str(self.name) + '/'
		if not os.path.exists(serverPath):
			os.mkdir(serverPath)


	def printLog(self, entry, log_file):
		'''
		prints a message to the console, and to a log file
		'''
		time_stamp = time.strftime('%H:%M:%S')
		log_file = str(log_file)
		print entry
		with open(log_file, 'a') as f:
			f.write('[' + str(time_stamp) + '] ' + entry + '\n')


	def on_connect(self, client):
		"""
		on_connect function.
		Handles new connections.
		"""
		playerDataID = str(client.addrport())
		self.printLog( "++ Opened connection to %s" % client.addrport(), self.log_file ) #need a printLog function
		#self.broadcast('%s connected.\n' % client.addrport() )
		self.cc.append(client)

		clientID = self.id_counter
		self.id_counter += 1

		clientInfo = ClientInfo.ClientInfo(owner=self, name='none', prompt='>>', client=client, ID=clientID, player_data_ID=playerDataID)
		self.pd[playerDataID] = clientInfo
		self.pd[playerDataID].loadFinish = False        #holds information about if login is complete
		self.pd[playerDataID].authSuccess = False       #holds information about the success of login attempts
		self.pd[playerDataID].numTries = 0              #the number of login attempts.

		# client.send("\n  ____________" + (len(self.name) * "_") + "__\n")
		client.send_cc("\n ^I  Welcome to ^!" + self.name + "^~^I!  ^~\n\n")
		# client.send(" |____________" + (len(self.name) * "_") + "__|\n\n")
		client.send("Please tell us your name.\n%s" % str(self.pd[playerDataID].prompt))


	def on_disconnect(self, client):
		"""
		on_disconnect function.
		Handles lost connections.
		"""
		playerDataID = str(client.addrport())

		self.pd[playerDataID].saveToFile()

		self.printLog( "-- Lost connection to %s" %playerDataID, self.log_file )

		self.cc.remove(client)
		del self.pd[playerDataID]

		# player = self.pd[playerDataID].avatar
		# if player is not None:
			#SysInit.clientDataSave(client, CLIENT_LIST, CLIENT_DATA, TIMERS)
			#player.currentRoom.players.remove(player)
			#alert(client, CLIENT_DATA, ("\n^g%s disappeared.^~\n" %player.name))


		self.broadcast('%s leaves the conversation.\n' % playerDataID )


	def kickIdle(self):		#probably boken atm
		"""
		Looks for idle clients and disconnects them by setting active to False.
		"""
		## Who hasn't been typing?
		for client in self.cc:
			player = self.pd[str(client.addrport())]
			if client.idle() > self.idle_timeout and player.gameState != 'battle':
				self.printLog('>> Kicking (%s)%s from server. (idle)' %(player.ID, player.name), self.log_file )
				#SysInit.clientDataSave(client, CLIENT_LIST, CLIENT_DATA, TIMERS)
				client.send_cc("You have been kicked for inactivity.\n")
				client.active = False


	def broadcast(self, msg):
		"""
		Send msg to every client.
		"""
		for client in self.cc:
			client.send_cc(msg + "\n")
			self.printLog("   " + msg, self.log_file)


	def stateCheck(self):
		'''
		check to see if the server is running
		'''
		if self.engine_state == 'shutdown':
			#print engineState
			# SysInit.dataSave(CLIENT_LIST, CLIENT_DATA, TIMERS)
			# RoomInit.saveAllRooms()
			# MobInit.saveMobs()
			# Objects.saveEq()
			self.printLog("<< Server shutdown.", self.log_file)
			self.server_run = False




#------------------------------------------------------------------------------
#       Main
#------------------------------------------------------------------------------


if __name__ == '__main__':

	## Create a telnet server with a port, address,
	## a function to call with new connections
	## and one to call with lost connections.
	server = Server()
	

	print( ">> Listening for connections on port %d.  CTRL-C to break." % server.TelnetServer.port )


	## Server Loop
	server.RUN()

