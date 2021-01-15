import requests
import time
from threading import Thread

with open("hypixel_api_key.txt", "r") as player_file:
    contents = player_file.read().split()

api_key = contents[0]

output = []

def get_player(player):
    data = requests.get(f"https://api.hypixel.net/player?key={api_key}&name={player}").json()["player"]

    lastLogin = data["lastLogin"]/1000
    lastLogoff = data['lastLogout']/1000

    if lastLogin - lastLogoff < 0:
        return ["Offline", ]

    secondsOnline = time.time()-lastLogin


    if secondsOnline < 3600:
        return ["Online", f"{round(secondsOnline/60)} minutes"]
    else:
        return ["Online", f"{round(secondsOnline/3600)} hours"]


def check(contents):
    global output

    output = []
    threads = []

    for uuid in contents:
        threads.append(Thread(target=doUUID, args=(uuid, )))

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    x = output

    return x



def doUUID(uuid):
    global output
    ign = requests.get(f"https://api.mojang.com/user/profiles/{uuid}/names").json()[-1]["name"]
    status = get_player(ign)
    if status[0] == "Online":
        output.append([ign, status[1]])



