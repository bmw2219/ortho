import discord
from discord.ext import commands, tasks
import asyncio
import requests
import datetime
import who_on_smp as smp
import who_on_hypixel as hypixel
import who_on_wynn as wynn
import json
import random
import schedule
import img_grabber

intents = discord.Intents.default()
intents.members = True
client = commands.Bot(command_prefix='!', intents=intents)

@client.event
async def on_ready():
    print('Bot is ready')
    doStuff.start()

async def saveAllStats():
    hypixel.saveAllStats()
# schedule.every().day.at("23:59").do(saveAllStats)

@tasks.loop(minutes=1)
async def doStuff():
    # schedule.run_pending()
    hypixel.updatePlaytimes()

@client.command(pass_context=True)
async def registered(ctx):
    async with ctx.typing():
        msg = "```\n"

        with open("registered_players.txt", "r") as player_file:
            contents = player_file.read().split()

        for uuid in contents:
            msg += requests.get(f"https://api.mojang.com/user/profiles/{uuid}/names").json()[-1]["name"]+"\n"

        msg += "```"

        await ctx.send(msg)

@client.command(pass_context=True)
async def megabran(ctx):
    # await ctx.send(file=discord.File("resources/megabran.jpg"))
    await ctx.send("no")
@client.command(pass_context=True)
async def register(ctx, ign):
    if ign is None:
        return 0
    player_data = requests.get("https://api.mojang.com/users/profiles/minecraft/"+ign)
    if player_data.status_code != 200:
        await ctx.send("error")
        return 0
    player_data = player_data.json()

    uuid = player_data["id"]

    with open("registered_players.txt", "r") as player_file:
        contents = player_file.read().split()

        if contents.count(uuid) == 0:
            with open("registered_players.txt", "a") as players_file:
                players_file.write("\n"+uuid)
                players_file.close()

    await ctx.send("User registered.")

@client.command(pass_context=True)
async def boop(ctx, who: discord.User):
    if who is None:
        await ctx.send("Who u boopin???")
        return

    await ctx.send(who.mention+" ***YOU*** have been booped!!!!!!")

@client.command(pass_context=True)
async def sumograss(ctx):
    wins = hypixel.getGrasSumoWins()
    image_path = img_grabber.getGars(wins)

    await ctx.send(file=discord.File(image_path))

# @client.command(pass_context=True)
# async def index(ctx):
#     name = str(random.randint(0,999999))
#     with open("indexes/"+name+".txt", "a+") as outfile:
#         async for msg in ctx.message.channel.history(limit=10000):
#             if len(msg.content)>0:
#                 try:
#                     outfile.write(msg.content+"\n")
#                 except UnicodeEncodeError:
#                     pass
#     await ctx.send("Channel Indexed ;)")

@client.command(pass_context=True)
async def online(ctx):
    async with ctx.typing():

        with open("registered_players.txt", "r") as player_file:
            contents = player_file.read().split()
        # wynn_gorls = wynn.check(contents)
        wynn_gorls = []
        hypixel_peeps = hypixel.check(contents)
        # smp_peeps = smp.getOnline()
        smp_peeps = []

        embed = discord.Embed(title="Hypixel", color=0x00ff4c)
        embed.set_thumbnail(url="https://hypixel.net/attachments/hypixel-jpg.760131/")
        for dude in hypixel_peeps:
            embed.add_field(name=f"🟢 {dude[0]}", value=f"Online for {dude[1]}", inline=False)
        if len(hypixel_peeps) == 0:
            embed.add_field(name=f"hmmm", value=f"nobody online :(", inline=False)

        '''mp_embed = discord.Embed(title="Hiley SMP", color=0x00ff4c)
        smp_embed.set_thumbnail(url="https://i.imgur.com/8xmL8fo.png")
        for person in smp_peeps:
            smp_embed.add_field(name=f"🟢 {person}", value=f"Online", inline=False)
        if len(smp_peeps) == 0:
            smp_embed.add_field(name=f"hmmm", value=f"nobody online :(", inline=False)'''

        '''wynn_embed = discord.Embed(title="Wynn", color=0x00ff4c)
        wynn_embed.set_thumbnail(url="https://cdn.wynncraft.com/img/wynn.png")
        for gorl in wynn_gorls:
            wynn_embed.add_field(name=f"🟢 {gorl[0]}", value=f"Online: {gorl[1]}", inline=False)
        if len(wynn_gorls) == 0:
            wynn_embed.add_field(name=f"hmmm", value=f"nobody online :(", inline=False)'''

        if len(hypixel_peeps) > 0:
            await ctx.send(embed=embed)
        else:
            await ctx.send("Nobody on Hypixel :((")

        if len(wynn_gorls) > 0:
            await ctx.send(embed=wynn_embed)
        else:
            await ctx.send("Wynn checking system down :((")

        if len(smp_peeps) > 0:
            await ctx.send(embed=smp_embed)
        else:
            await ctx.send("SMP Offline :((")




        return 0

'''@client.command(pass_context=True)
async def makeTeky(ctx):
    newName = ctx.message.content.replace("!makeTeky ", "")
    if len(newName.strip())==0:
        return
    teky = ctx.guild.get_member(258048636653535234)
    await teky.edit(nick=newName)
    await ctx.send("Teky is now "+newName)'''

@client.command(pass_context=True)
async def playtime(ctx, player):
    async with ctx.typing():
        with open("registered_players.txt", "r") as player_file:
            contents = player_file.read().split()
        registered = False
        for uuid in contents:
            name = requests.get(f"https://api.mojang.com/user/profiles/{uuid}/names").json()[-1]["name"]
            if name.lower() == player.lower():
                registered = True
                player = name
                player_uuid = uuid
                break
        if registered is False:
            await ctx.send("That player is not registered with Ortho.\nPlease use \"!register <player>\" to register someone.")
            return

        date = datetime.datetime.now().strftime(format="%m/%d/%y")
        dash_date = datetime.datetime.now().strftime(format="%m-%d-%y")

        with open(f"stat_files/playtimes/{dash_date}.json") as file:
            minsPlayed = json.load(file)[player_uuid]

        img = img_grabber.playtime(player, player_uuid, date, minsPlayed, "Today")

        await ctx.send(file=discord.File(img))

@client.event
async def on_message(msg):
    '''if msg.content == "oh":
        secondOh = msg.author
        if secondOh.bot:
            return
        async for msg in msg.channel.history(limit=2):
            if msg.content == "oh" and msg.author.bot is False and msg.author is not secondOh:
                firstOh = msg.author
            else:
                return

        await asyncio.sleep(0.5)
        await msg.channel.send("oh")
    elif msg.content == "man":
        secondOh = msg.author
        if secondOh.bot:
            return
        async for msg in msg.channel.history(limit=2):
            if msg.content == "man" and msg.author.bot is False and msg.author is not secondOh:
                firstOh = msg.author
            else:
                return

        await asyncio.sleep(0.5)
        await msg.channel.send("man")'''
    if random.randint(0,1000)==69:
        await msg.channel.send("yes")
    if msg.content.count(":teky:") > 0:
        await msg.channel.send("smh my head i can't believe you just tried that")

    await client.process_commands(msg)


with open("bot_key.txt", "r") as player_file:
    key = player_file.read().split()

client.run(key[0])
