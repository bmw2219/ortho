import discord
from discord.ext import commands
import requests
import who_on_smp as smp
import who_on_hypixel as hypixel
import who_on_wynn as wynn

client = commands.Bot(command_prefix='!')

@client.event
async def on_ready():
    print('Bot is ready')

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
async def online(ctx):
    async with ctx.typing():

        with open("registered_players.txt", "r") as player_file:
            contents = player_file.read().split()
        wynn_gorls = wynn.check(contents)
        hypixel_peeps = hypixel.check(contents)
        smp_peeps = smp.getOnline()

        embed = discord.Embed(title="Hypixel", color=0x00ff4c)
        embed.set_thumbnail(url="https://hypixel.net/attachments/hypixel-jpg.760131/")
        for dude in hypixel_peeps:
            embed.add_field(name=f"🟢 {dude[0]}", value=f"Online for {dude[1]}", inline=False)
        if len(hypixel_peeps) == 0:
            embed.add_field(name=f"hmmm", value=f"nobody online :(", inline=False)

        smp_embed = discord.Embed(title="Hiley SMP", color=0x00ff4c)
        smp_embed.set_thumbnail(url="https://i.imgur.com/8xmL8fo.png")
        for person in smp_peeps:
            smp_embed.add_field(name=f"🟢 {person}", value=f"Online", inline=False)
        if len(smp_peeps) == 0:
            smp_embed.add_field(name=f"hmmm", value=f"nobody online :(", inline=False)

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

        if len(smp_peeps) > 0:
            await ctx.send(embed=smp_embed)
        else:
            await ctx.send("Nobody on the SMP :((")

        if len(wynn_gorls) > 0:
            await ctx.send(embed=wynn_embed)
        else:
            await ctx.send("Nobody on Wynn :((")


        return 0

with open("bot_key.txt", "r") as player_file:
    key = player_file.read().split()

client.run(key[0])
