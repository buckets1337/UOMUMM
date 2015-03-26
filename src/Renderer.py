# Renderer.py
# Various ways to format text output to players

class Renderer():
	'''
	A renderer component just contains methods for formatting text output in various ways
	'''
	def __init__(self, server):
		self.owner = server


	def formatMessage(self, message, width):
		'''
		splits a <message> string into lines that are <width> characters long without breaking words 
		apart across lines. Broken apart single lines are slightly indented on every line other than 
		the first in the final formatted message.
		Returns the formatted message string. 
		'''
		count = 0
		formatted = ''
		if message == None:
			message = 'None'
		for character in range(0,len(message)):
			char = message[character]
			if char != '\n':
				if count < width:
					formatted += char
					count += 1
					#print formatted
				else:
					if message[character] == ' ':
						formatted += "\n" + char
						count = 2
						#print 'da TRUTH'
					else:
						collecting = True
						coll = ''
						i = 1
						while collecting:
							if message[character-i] != '\n':
								coll += message[character-i]
								i += 1
							else:
								collecting = False
						if ' ' not in coll.strip():
							#print 'TRUE'
							formatted += "\n " + char
							count = 2
						else:
							#print 'checking...'
							checking = True
							i = 1
							while checking:
								msg = message.strip()
								chk = msg[character-i]
								#print chk
								if chk == ' ':
									#print formatted
									formatted = formatted[:-i] + "\n" + formatted[-i:] + char
									#print formatted
									count = i + 1
									checking = False
								else:
									i += 1


			else:
				formatted += char
				count = 0

		return formatted


	def messageBox(self, client, title, message):
		'''
		displays a simple <message> in a box for <client>.
		The box resizes to fit the message and title.
		Has a <title> at the top of the box along the border.
		'''
		message = self.formatMessage(message, 76)
		#print message
		if message.endswith("\n"):
			message = message[:-1]
		msgLines = message.split('\n')
		#print msgLines
		finalMsg = ''
		longest = 0
		for line in msgLines:
			if len(line) > longest:
				longest = len(line)
		for line in msgLines:
			if longest > len(str(title)):
				if longest > len(line):
					mod = longest - len(line)
					line = line + ((mod) * " ")
				# else:
				# 	line = line + ((len(str(title)) - 4) * " ")
			else:
				mod = (len(str(title)) + 2) - len(line) 
				line = line + (mod * " ")
			line = " | " + line + " |\n"
			finalMsg += line

		#print int((0.5)*float(longest))
		if longest >= len(str(title)):
			titleLine = "\n  " + (int((0.5)*float(longest - len(str(title)))+1)* "_") + "^!"+str(title)+"^~" + (int((0.5)*float(longest - len(str(title)))+1)* "_") + "\n"
			titleLineLen = len(titleLine) - 6
			if titleLineLen > (longest + 2):
				#print len(titleLine)
				#print longest + 2
				diff = titleLineLen - (longest + 2) - 1
				if not diff <= 0:
					titleLine = titleLine[:-diff] + "\n"
				if diff == 0:
					titleLine = titleLine[:-1] + "_\n"
			elif (longest + 2) >= titleLineLen:
				diff = (longest + 2) - titleLineLen
				if titleLine.endswith("\n"):
					titleLine = titleLine[:-1]
				titleLine += (diff * "_") + "\n"

			client.send_cc(titleLine)
			client.send_cc(" |" + ((longest + 2)*" ") + "|\n")
			client.send_cc(finalMsg)
			client.send_cc(" |" + ((longest + 2)*"_") + "|\n\n")
		else:
			client.send_cc("\n  __^!" + str(title) + "^~__\n")
			client.send_cc(" |" + ((4 + len(str(title))) * " ") + "|\n")
			client.send_cc(finalMsg)
			client.send_cc(" |" + ((4 + len(str(title))) * "_") + "|\n\n")


	def roomDisplay(self, client, room):
		'''
		renders the typical display for a room to client
		'''

		namePad = 80 - len(room.name) - 2

		client.send_cc("\n")
		message = "+" + ("-" * (int(0.5 *namePad)-1)) + "^! " + str(room.name) + " ^~" + ("-" * (int(0.5* namePad)-1)) + "+" + "\n"
		if len(message) < 81:
			message = "+" + ("-" * (int(0.5 *namePad)-1)) + "^! " + str(room.name) + " ^~" + ("-" * (int(0.5* namePad)-1)) + "-+" + "\n"
		client.send_cc(message)
		# client.send_cc("|" + (" " * 78) + "|" + "\n")

		descrip = self.formatMessage(room.description, 76)
		desc = descrip.split("\\n")
		#print desc
		for line in desc:
			linePad = 80 - len(line) - 2
			if len(line) > 0:
				message = "|" +(" " * (int(0.5 *linePad))) + line +(" " * (int(0.5 *linePad))) + "|" + "\n"
				if len(message) < 81:
					message = ("|" +(" " * (int(0.5 *linePad))) + line +(" " * (int(0.5 *linePad))) + " |" + "\n")
				client.send_cc(message)

			else:
				client.send_cc("|" + (" " * 78) + "|" + "\n")
		client.send_cc("+" + ("-" * 78) + "+" + "\n")

		client.send_cc("|" + (" " * 78) + "|" + "\n")
		#print "players: " + str(room.players)
		for player in room.players:
			if player.connection != client:
				playerPad = int(80 - len(player.name) - 3)
				client.send_cc("| " + "^C" + str(player.name) + "^~" + (" " * playerPad) + "|" + "\n")
			else:
				client.send_cc("|" + (" " * 78) + "|" + "\n")
		client.send_cc("|" + (" " * 78) + "|" + "\n")

		client.send_cc("|" + (" " * 78) + "|" + "\n")
		exitList = []
		if room.orderedExits == []:
			#print 'test'
			#print room.exits
			for exit in room.exits:
				#print room.exits[exit]
				exitList.append(str(room.exits[exit]))
			room.orderedExits = exitList
		else:
			for rm in room.orderedExits:
				exitList.append(str(rm[1]))
		#print exitList
		if exitList != []:
			lenExit = len(exitList[0])
		else:
			lenExit = 0
		firstPad = int(80 - lenExit - 12)
		if exitList != []:
			msg = "| " + "^!exits:^~ 1." + exitList[0] + (" " * firstPad) + "|" + "\n"
			client.send_cc(msg)
			i = 2
			for exit in exitList[1:]:
				pad = int(80 - len(exitList[i-1]) - 12)
				client.send_cc("|        " + str(i) + "." + exitList[i-1] + (" " * pad) + "|" + "\n")
				i += 1
		else:
			client.send_cc("|" + (" " * 78) + "|" + "\n")
		client.send_cc("+" + ("-" * 78) + "+" + "\n")