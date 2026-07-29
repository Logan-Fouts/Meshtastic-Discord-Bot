import queue

# Messages coming FROM the mesh network, TO be sent to Discord (str or discord.Embed)
meshtodiscord = queue.Queue()

# Messages coming FROM Discord commands, TO be sent to the mesh network (str)
discordtomesh = queue.Queue()

# Signal queue: presence of an item means "please post the current node list"
nodelistq = queue.Queue()