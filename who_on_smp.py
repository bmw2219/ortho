from mcstatus import MinecraftServer

server = MinecraftServer("2.tcp.ngrok.io", port=11186)

def getOnline():
    status = server.status()
    playersList = []

    try:
        for dude in status.players.sample:
            playersList.append(dude.name)
    except TypeError:
        pass

    return playersList