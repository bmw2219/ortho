import discord
from discord.ext import commands, tasks
import requests
import datetime
import speak
# import who_on_smp as smp
import asyncio
import who_on_hypixel as hypixel
import who_on_wynn as wynn
import json
import random
import interpreter
import date_grabber as dates
from tictactoe import *
import leaderboards
import img_grabber

intents = discord.Intents.default()
intents.members = True
client = commands.Bot(command_prefix='!', intents=intents)


@client.event
async def on_ready():
    print('Bot is ready')
    doStuff.start()


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
async def lonely(ctx):
    words = "hey baby its ortho im here for you smile heart emoji" if len(ctx.message.content.split()) == 1 else ctx.message.content[8:]

    channel = ctx.author.voice.channel
    vc = await channel.connect()
    # await ctx.send("im here for u bb <3")
    vc.play(discord.FFmpegPCMAudio(speak.get_tts(words)))
    while vc.is_playing():
        await asyncio.sleep(1)
    await vc.disconnect()

@client.command(pass_context=True)
async def quote(ctx):
    names = ctx.message.content.split()[1:]
    placeholders = ["{A}", "{B}", "{C}", "{D}", "{E}", "{F}"]
    with open("quotes.json", encoding="utf8") as json_file:
        quote_list = json.load(json_file)["quotes"][len(names)-1]

    header = "**ScatterPatter's Incorrect Quotes Generator**\n\n"
    quote = quote_list[random.randint(0, len(quote_list)-1)]
    quote = quote.replace("<br>", "\n")
    quote = quote.replace("*", "\\*")
    quote = quote.replace("<i>", "*")
    quote = quote.replace("</i>", "*")
    for i, item in enumerate(placeholders):
        if quote.count(item) > 0:
            quote = quote.replace(item, f"{names[i]}")
    quote = header + quote
    # embed = discord.Embed(title="ScatterPatter's Incorrect Quotes Generator",
    #                       url="https://incorrect-quotes-generator.neocities.org/",
    #                       description=quote)
    # embed.add_field(name=quote, value="Check out the website :D", inline=True)

    quote += f"\n\nAll quotes taken from: https://incorrect-quotes-generator.neocities.org/"
    await ctx.send(quote)


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

@client.command(pass_context=True)
async def dailybw(ctx):
    args = ctx.message.content.split()
    date_string = f"{args[0]} {args[1]} "

    if len(args) > 2 and dates.getDate(ctx.message.content.replace(date_string, "", 1))[0]:
        date_string = (dates.getDate(ctx.message.content.replace(date_string, "", 1))[1] - datetime.timedelta(days=1)).strftime(format="%m-%d-%y")
    elif ctx.message.content.replace(date_string[:-1], "", 1) == "":
        date_string = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime(format="%m-%d-%y")
    elif dates.getDate(ctx.message.content.replace(date_string, "", 1))[0] is False:
        await ctx.send("Invalid Date")
        return
    ds = f"{args[0]} {args[1]} "
    final_date = datetime.datetime.now().strftime(format="%m/%d/%y") if ctx.message.content.replace(ds[:-1], "", 1) == "" or args[2] == "today" else dates.getDate(ctx.message.content.replace(ds, "", 1))[1].strftime(format="%m/%d/%y")



    if len(args) == 1:
        await ctx.send("**Format:** !dailybw <player>\n\n**NOTE:** The target player must be registered with Ortho.\nDo !register <player> to register someone")
        return

    with open("registered_players.txt", "r") as player_file:
        contents = player_file.read().split()

    player = args[1]
    if len(args) > 2 and \
            dates.getDate(ctx.message.content.replace(f"{args[0]} {args[1]}", "", 1))[0] and \
            dates.getDate(ctx.message.content.replace(f'{args[0]} {args[1]}', '', 1))[1].strftime(format='%m-%d-%y') != datetime.datetime.today().strftime(format='%m-%d-%y'):

        player_data = requests.get("https://api.mojang.com/users/profiles/minecraft/" + player)
        if player_data.status_code != 200:
            await ctx.send("error")
            return 0
        player_data = player_data.json()
        uuid = player_data["id"]
        with open(f"stat_files/allStats/{dates.getDate(ctx.message.content.replace(f'{args[0]} {args[1]}', '', 1))[1].strftime(format='%m-%d-%y')}/{uuid}.json") as file:
            current_data = json.load(file)

    else:
        current_data = hypixel.getPlayerData(args[1])

    if current_data["player"] is None:
        await ctx.send("Invalid Username")
        return

    current_data = current_data["player"]
    uuid = current_data["uuid"]
    player = current_data["displayname"]

    if uuid not in contents:
        await ctx.send("That player is not registered with Ortho.\n\nDo !register <player> to register a player.")
        return

    with open(f"stat_files/allStats/{date_string}/{uuid}.json") as file:
        past_data = json.load(file)["player"]

    levels = current_data['achievements']['bedwars_level'] - past_data['achievements']['bedwars_level']
    wins = current_data['stats']['Bedwars']['wins_bedwars'] - past_data['stats']['Bedwars']['wins_bedwars']
    losses = current_data['stats']['Bedwars']['losses_bedwars'] - past_data['stats']['Bedwars']['losses_bedwars']
    final_kills = current_data['stats']['Bedwars']['final_kills_bedwars'] - past_data['stats']['Bedwars']['final_kills_bedwars']
    final_deaths = current_data['stats']['Bedwars']['final_deaths_bedwars'] - past_data['stats']['Bedwars']['final_deaths_bedwars']
    kills = current_data['stats']['Bedwars']['kills_bedwars'] - past_data['stats']['Bedwars']['kills_bedwars']
    deaths = current_data['stats']['Bedwars']['deaths_bedwars'] - past_data['stats']['Bedwars']['deaths_bedwars']
    beds_broken = current_data['stats']['Bedwars']['beds_broken_bedwars'] - past_data['stats']['Bedwars']['beds_broken_bedwars']
    beds_lost = current_data['stats']['Bedwars']['beds_lost_bedwars'] - past_data['stats']['Bedwars']['beds_lost_bedwars']

    output_txt = f"DAILY STATS (**{final_date}**)\n" \
                 f"```---------------------------\n" \
                 f"Player: {player}\n" \
                 f"Levels Gained: {levels}\n" \
                 f"Wins: {wins}\n" \
                 f"Losses: {losses}\n" \
                 f"Games Played: {wins+losses}\n" \
                 f"WLR: {round(wins/losses, 2) if losses > 0 else wins}\n\n" \
                 f"Final Kills: {final_kills}\n" \
                 f"Final Deaths: {final_deaths}\n" \
                 f"FKDR: {round(final_kills/final_deaths, 2) if final_deaths > 0 else final_kills}\n" \
                 f"FK/G: {round(final_kills/(wins+losses), 2) if (wins+losses) > 0 else 0}\n\n" \
                 f"Kills: {kills}\n" \
                 f"Deaths: {deaths}\n" \
                 f"KDR: {round(kills/deaths, 2) if deaths > 0 else kills}\n" \
                 f"K/G: {round(kills/(wins+losses), 2) if (wins+losses) > 0 else 0}\n\n" \
                 f"Beds Broken: {beds_broken}\n" \
                 f"Beds Lost: {beds_lost}\n" \
                 f"BBLR: {round(beds_broken/beds_lost, 2) if beds_lost > 0 else beds_broken}\n" \
                 f"B/G: {round(beds_broken/(wins+losses), 2) if (wins+losses) > 0 else 0}```"

    await ctx.send(output_txt)


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
async def calc(ctx):
    args = ctx.message.content.split()
    if len(args) == 1:
        await ctx.send("**Correct Format**: !calc <equation>\n\n"
                       "*This command is used to make/test basic PEMDAS calculations using Ortho's equation interpreter.*")

    equation = ctx.message.content.replace("!calc ", "", 1)

    answer = round(float(interpreter.interpret(values={}, equation=equation)), 4)

    await ctx.send(f"```\n{equation}\nAnswer: {answer}\n```")


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
        try:
            wynn_gorls = wynn.check(contents)
            # wynn_gorls = []
            hypixel_peeps = hypixel.check(contents)
            # smp_peeps = smp.getOnline()
            smp_peeps = []
        except KeyError:
            await ctx.send("Sorry, there's too many API requests right now. Please wait ~1 minute before trying again")
            return

        embed = discord.Embed(title="Hypixel", color=0x00ff4c)
        embed.set_thumbnail(url="https://hypixel.net/attachments/hypixel-jpg.760131/")
        for dude in hypixel_peeps:
            embed.add_field(name=f"🟢 {dude[0]}", value=f"{dude[1]}\n{dude[2]}", inline=True)
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


game_boards = []
reactions = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"]
@client.command(pass_context=True, aliases=["ttt"],)
async def tictactoe(ctx, user: discord.User):
    players = [ctx.author, user]

    string = "---------"
    board = TictactoeBoard(string)
    random.shuffle(players)
    board.players = players
    output_string, reactions_used = board.toOutputBoard()

    current_player_turn = board.players[board.turnIndex % 2]

    board.board_message = await ctx.send(output_string)
    board.text_message = await ctx.send(f"<@!{current_player_turn.id}>, you go first! Choose a square through the reaction")

    game_boards.append(board)
    for i in reactions_used:
        await board.board_message.add_reaction(i)


@client.event
async def on_raw_reaction_add(payload):
    for i in range(len(game_boards)):
        if game_boards[i].board_message.id == payload.message_id and payload.member.bot is False:
            board = game_boards[i]
            current_player_turn = board.players[board.turnIndex % 2]
            brd, reactions_available = board.toOutputBoard()
            if payload.user_id != current_player_turn.id or str(payload.emoji) not in reactions_available:
                return
            buttonIndex = reactions.index(str(payload.emoji))
            board.makeMove(board.whos_turn, buttonIndex)
            new_board, reactions_used = board.toOutputBoard()
            results = board.checkForGame()
            symbols = ["❌", "⭕"]
            if results[0]:
                if results[1] == "Tie":
                    msg = f"<@!{board.players[0].id}> {symbols[0]} and <@!{board.players[1].id}> {symbols[1]} have tied!!"
                elif results[1] == "x":
                    msg = f"<@!{board.players[0].id}> {symbols[0]} has *destroyed* <@!{board.players[1].id}> {symbols[1]} in this respectable game of TICTACTOE!!!!"
                elif results[1] == "o":
                    msg = f"<@!{board.players[1].id}> {symbols[1]} has *destroyed* <@!{board.players[0].id}> {symbols[0]} in this respectable game of TICTACTOE!!!!"

                await board.board_message.clear_reactions()
                await board.board_message.edit(content=new_board)
                await board.text_message.edit(content=msg)
                return

            current_player_turn = board.players[board.turnIndex % 2]
            current_symbol = symbols[board.turnIndex % 2]



            await board.board_message.clear_reaction(payload.emoji)
            await board.board_message.edit(content=new_board)
            await board.text_message.edit(content=f"<@!{current_player_turn.id}> it is now your turn! You are {current_symbol} Choose a square through the reaction. ({board.turnIndex})")
            # for j in reactions_used:
            #     await games[i].add_reaction(j)



@client.event
async def on_message(msg):
    if random.randint(0,1000)==69:
        await msg.channel.send("yes")
    if msg.content.count(":teky:") > 0:
        await msg.channel.send("smh my head i can't believe you just tried that")

    await client.process_commands(msg)


with open("bot_key.txt", "r") as player_file:
    key = player_file.read().split()

client.run(key[0])
