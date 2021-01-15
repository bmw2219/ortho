import requests
import time
from threading import Thread

output = []

def get_player(player):
    old_player = player
    player = f"{old_player[:8]}-{old_player[8:12]}-{old_player[12:16]}-{old_player[16:20]}-{old_player[20:]}"

    data = requests.get(f"https://api.wynncraft.com/v2/player/{player}/stats").json()["data"]
    if len(data) == 0:
        return ["dhsfl", False]

    ign = data[0]["username"]
    online = data[0]["meta"]["location"]["online"]
    if online is False:
        return [ign, False, ]
    server = data[0]["meta"]["location"]["server"]
    return [ign, True, server]

def check(contents):
    global output
    output = []
    threads = []

    for uuid in contents:
        threads.append(Thread(target=doUUID, args=(uuid,)))

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    x = output

    return x


def doUUID(uuid):
    global output

    data = get_player(uuid)
    if data[1]:
        output.append([data[0], data[2]])

print(get_player("56977856afa34a3e8e645c1a6ba1ccae"))