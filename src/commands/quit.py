#quit.py
#the quit command

def quitCommand(engine, client, player):
	'''
	disconnects a player
	'''
	engine.owner.printLog("-- %s quit." %player.name, engine.owner.log_file)
	client.active = False