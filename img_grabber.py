from __future__ import print_function
import math
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
from io import BytesIO
import requests
import random


def getGars(wins):
    im = Image.open("resources/top.png")
    draw = ImageDraw.Draw(im)
    font = ImageFont.truetype("resources/Lato-Black.ttf", 65)
    draw.text((130, 100),str(wins),(255,255,255), font=font)
    # print(im.format, im.size, im.mode)
    name = "byproduct_files/"+str(random.randint(0,999999))+".png"
    im.save(name)
    return name

def playtime(player, uuid, date, minsPlayed, when):
    hours = math.floor(minsPlayed/60)
    minutes = minsPlayed % 60

    request = requests.get(f"https://mc-heads.net/body/{uuid}/left")
    player_model = Image.open(BytesIO(request.content))
    player_model = player_model.resize((round(player_model.size[0] * 0.4), round(player_model.size[1] * 0.4)))

    background = Image.open("resources/playtime_template.png")
    draw = ImageDraw.Draw(background)
    font = ImageFont.truetype("resources/Minecraftia_Regular.ttf", 15)
    draw.fontmode = "l"
    draw.text((90, 52), player, (0,255,0), font=font)
    draw.text((68,82), date, (0,255,0),font=font)
    draw.text((19, 142), str(hours), (0, 255, 0), font=font)
    draw.text((19, 175), str(minutes), (0, 255, 0), font=font)
    draw.text((62, 210), when, (0, 255, 0), font=font)
    background.paste(player_model, (333, 30), player_model)
    name = "byproduct_files/" + str(random.randint(0, 999999)) + ".png"
    background.save(name)
    return name

playtime("Teky1", "56977856afa34a3e8e645c1a6ba1ccae", "1/2/2021", 1000, "Today")