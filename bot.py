import discord
from discord.ext import commands, tasks
import asyncio
import requests
import datetime
# import who_on_smp as smp
import who_on_hypixel as hypixel
import who_on_wynn as wynn
import json
import random
import interpreter
import schedule
import leaderboards
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
async def bwscore(ctx, ign, equation):
    values = hypixel.getIGNBwStats(ign)
    score = round(float(interpreter.interpret(values, equation)), 2)
    op = "```\nBed Wars\n"
    op += f"Equation: {equation}\n"
    op += f"{ign}: {score}\n```"
    await ctx.send(op)

@client.command(pass_context=True)
async def mmscore(ctx, ign, equation):
    values = hypixel.getIGNMMStats(ign)
    score = round(float(interpreter.interpret(values, equation)), 2)
    op = "```\nMurder Mystery\n"
    op += f"Equation: {equation}\n"
    op += f"{ign}: {score}\n```"
    await ctx.send(op)

@client.command(pass_context=True, aliases=["bwlb"])
async def bedwarsleaderboard(ctx, equation):
    async with ctx.typing():
        with open("registered_players.txt", "r") as player_file:
            contents = player_file.read().split()
        all_stats = hypixel.getAllPlayerBwStats(contents)
        lb = leaderboards.leaderboard(all_stats, equation)
        output = f"```\nBed Wars\n{equation} leaderboards:\n"

        for i in range(len(lb)):
            output+=f"{i+1}. {lb[i][0]} ({lb[i][1]})\n"
        output += "```"
        await ctx.send(output)

@client.command(pass_context=True, aliases=["mmlb"])
async def mmleaderboard(ctx, equation):
    async with ctx.typing():
        with open("registered_players.txt", "r") as player_file:
            contents = player_file.read().split()
        all_stats = hypixel.getAllPlayerMMStats(contents)
        lb = leaderboards.leaderboard(all_stats, equation)
        output = f"```\nMurder Mystery\n{equation} leaderboards:\n"

        for i in range(len(lb)):
            output+=f"{i+1}. {lb[i][0]} ({lb[i][1]})\n"
        output += "```"
        await ctx.send(output)



@client.command(pass_context=True)
async def bwterms(ctx):
    await ctx.send("The available data for BW is: level, wins, losses, final_kills, final_deaths, kills, deaths, beds_broken, beds_lost")

@client.command(pass_context=True)
async def mmterms(ctx):
    await ctx.send("The available data for MM is: wins, losses, kills, deaths, gold_collected")



@client.command(pass_context=True)
async def sumograss(ctx):
    wins = hypixel.getGrasSumoWins()
    image_path = img_grabber.getGars(wins)

    await ctx.send(file=discord.File(image_path))


@client.command(pass_context=True, aliases=["fl"])
async def online(ctx):
    async with ctx.typing():

        with open("registered_players.txt", "r") as player_file:
            contents = player_file.read().split()
        wynn_gorls = wynn.check(contents)
        # wynn_gorls = []
        hypixel_peeps = hypixel.check(contents)
        # smp_peeps = smp.getOnline()
        smp_peeps = []

        embed = discord.Embed(title="Hypixel", color=0x00ff4c)
        embed.set_thumbnail(url="https://hypixel.net/attachments/hypixel-jpg.760131/")
        for dude in hypixel_peeps:
            embed.add_field(name=f"🟢 {dude[0]}", value=f"Online for {dude[1]}", inline=False)
        if len(hypixel_peeps) == 0:
            embed.add_field(name=f"hmmm", value=f"nobody online :(", inline=False)

        # smp_embed = discord.Embed(title="Hiley SMP", color=0x00ff4c)
        # smp_embed.set_thumbnail(url="https://i.imgur.com/8xmL8fo.png")
        # for person in smp_peeps:
        #     smp_embed.add_field(name=f"🟢 {person}", value=f"Online", inline=False)
        # if len(smp_peeps) == 0:
        #     smp_embed.add_field(name=f"hmmm", value=f"nobody online :(", inline=False)

        wynn_embed = discord.Embed(title="Wynn", color=0x00ff4c)
        wynn_embed.set_thumbnail(url="https://cdn.wynncraft.com/img/wynn.png")
        for gorl in wynn_gorls:
            wynn_embed.add_field(name=f"🟢 {gorl[0]}", value=f"Online: {gorl[1]}", inline=False)
        if len(wynn_gorls) == 0:
            wynn_embed.add_field(name=f"hmmm", value=f"nobody online :(", inline=False)

        if len(hypixel_peeps) > 0:
            await ctx.send(embed=embed)
        else:
            await ctx.send("Nobody on Hypixel :((")

        if len(wynn_gorls) > 0:
            await ctx.send(embed=wynn_embed)
        else:
            await ctx.send("Nobody on Wynn :((")

        if len(smp_peeps) > 0:
            # await ctx.send(embed=smp_embed)
            pass
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

def isRegistered(ign):
    with open("registered_players.txt", "r") as player_file:
        contents = player_file.read().split()
    registered = False
    for uuid in contents:
        name = requests.get(f"https://api.mojang.com/user/profiles/{uuid}/names").json()[-1]["name"]
        if name.lower() == ign.lower():
            registered = True
            return [True, name, uuid]
    return [False,]

def getPlaytime(uuid, datetime_obj):
    dash_date = datetime_obj.strftime(format="%m-%d-%y")
    with open(f"stat_files/playtimes/{dash_date}.json") as file:
        minsPlayed = json.load(file)[uuid]
    return minsPlayed

@client.command(pass_context=True)
async def playtime(ctx, player):
    async with ctx.typing():
        args = ctx.message.content.split()
        if len(args) == 2:
            registerInfo = isRegistered(player)
            if registerInfo[0] is False:
                await ctx.send("That player is not registered with Ortho.\nPlease use \"!register <player>\" to register someone.\n\n**Note**: It can take up to 24 hours after registering a user for any playtime functionality to work.")
                return
            player = registerInfo[1]
            player_uuid = registerInfo[2]
            date = datetime.date.today()
            minsPlayed = getPlaytime(player_uuid, date)
            img = img_grabber.playtime(player, player_uuid, date.strftime(format="%m/%d/%y")+" (Today)", minsPlayed, "Today")
            await ctx.send(file=discord.File(img))
        else:
            if args[2].lower() == "yesterday":

                date = datetime.date.today() - datetime.timedelta(days=1)

                registerInfo = isRegistered(player)
                if registerInfo[0] is False:
                    await ctx.send("That player is not registered with Ortho.\nPlease use \"!register <player>\" to register someone.")
                    return
                player = registerInfo[1]
                player_uuid = registerInfo[2]
                minsPlayed = getPlaytime(player_uuid, date)
                img = img_grabber.playtime(player, player_uuid, datetime.date.today().strftime(format="%m/%d/%y")+" (Today)", minsPlayed, f"Yesterday ({date.strftime(format='%m/%d/%y')})")
                await ctx.send(file=discord.File(img))
            else:
                await ctx.send("")
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
