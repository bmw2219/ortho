import requests
import time
import json
import datetime
import os
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

def returnName(uuid):
    ign = requests.get(f"https://api.mojang.com/user/profiles/{uuid}/names").json()[-1]["name"]
    return ign

def saveAllStats():
    date_ = datetime.datetime.now().strftime(format="%m-%d-%y")
    try:
        os.mkdir(f"stat_files/allStats/{date_}")
    except FileExistsError:
        pass
    with open("registered_players.txt", "r") as player_file:
        contents = player_file.read().split()
    for uuid in contents:
        ign = returnName(uuid)
        data = requests.get(f"https://api.hypixel.net/player?key={api_key}&name={ign}").json()

        with open(f"stat_files/allStats/{date_}/{uuid}.json", "w") as outfile:
            json.dump(data, outfile)

def updatePlaytimes():
    date_ = datetime.datetime.now().strftime(format="%m-%d-%y")
    with open("registered_players.txt", "r") as player_file:
        contents = player_file.read().split()
    try:
        with open(f"stat_files/playtimes/{date_}.json", "r") as file:
            ze_data = json.load(file)
    except FileNotFoundError:
        ze_data = {}
        for i in contents:
            ze_data[i] = 0

    for uuid in ze_data:
        try:
            thing = get_player(returnName(uuid))
        except json.decoder.JSONDecodeError:
            # print("that error happened")
            pass


        if thing[0]=="Online":
            ze_data[uuid] += 1

    with open(f"stat_files/playtimes/{date_}.json", "w") as file:
        json.dump(ze_data, file)
        # print("dumped at "+datetime.datetime.now().strftime("%H:%M:%S"))


def getGrasSumoWins():
    data = requests.get(f"https://api.hypixel.net/player?key={api_key}&name=Grassias").json()["player"]["stats"]["Duels"]["sumo_duel_wins"]
    return data