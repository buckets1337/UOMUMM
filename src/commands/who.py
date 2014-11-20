#who.py
#the who command

def whoCommand(engine, client, player):
	'''
	shows the currently logged on players
	'''
	playerNames = ''
	for player in engine.owner.pd:
		playerNames += engine.owner.pd[player].name + '\n'
	engine.owner.Renderer.messageBox(client, 'Currently Connected Players', playerNames)