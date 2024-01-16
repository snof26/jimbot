import discord
from discord.ext import commands, tasks
from discord import Intents
import random
import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import openpyxl as op
import asyncio
from ossapi import Ossapi
from mcstatus import JavaServer
import os
import pytz
import json

# hypixel api key = 81453960-b772-411d-8f95-9e79934e9ddf


# initialising bot
intents = discord.Intents.all()
intents.message_content = True
intents.voice_states = True
client = commands.Bot(command_prefix="jim ", intents = intents)

# Remove the default help command
client.remove_command("help")

async def load_extensions():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            try:
                await client.load_extension(f'cogs.{filename[:-3]}')
                print(f'Loaded extension: {filename[:-3]}')
            except commands.ExtensionAlreadyLoaded:
                print(f'Extension already loaded: {filename[:-3]}')
            except commands.ExtensionNotFound:
                print(f'Extension not found: {filename[:-3]}')
            except commands.NoEntryPointError:
                print(f'No setup function found in: {filename[:-3]}')

# checking if logged in
@client.event
async def on_ready():
    print("logged in")
    
    # phoenix 2 daily missions event
    async def func():
        await client.wait_until_ready()
        priv = client.get_channel(1066341871502241953)
        minick = client.get_channel(742686837612609599)
        await minick.send("phoenix 2 daily missions")

    channel = client.get_channel(742686837612609599)
    # Initializing scheduler
    scheduler = AsyncIOScheduler(timezone="Australia/Sydney")
    # executes function at 11:00 (Local Time)
    scheduler.add_job(func, CronTrigger(hour="11", minute="0", second="0")) 
    # Starting the scheduler
    scheduler.start()
    print("scheduler on")
    await load_extensions()
    await client.change_presence(activity=discord.Game(name="Phoenix 2"))

@client.command()
async def wang(ctx):
    client_id = 20478
    client_secret = "D8MFcn2VtiiW798NN2oIgvRpPj1VYVkDkvTVaorx"
    api = Ossapi(client_id, client_secret)
    user = api.user("JK BOMBER")
    link = "https://osu.ppy.sh/users/14737026"
    avatar = user.avatar_url
    location = user.country.name
    username = user.username
    crank = user.statistics.country_rank
    grank = user.statistics.global_rank
    level = user.statistics.level.current
    pp = user.statistics.pp
    acc = user.statistics.hit_accuracy
    online = user.is_online

    tz = pytz.timezone('Australia/Melbourne')
    last_visit = user.last_visit
    last_visit_utc10 = last_visit.astimezone(tz)
    last_visit_utc10_formatted = last_visit_utc10.strftime('%H:%M')

    if online == True:
        footer = "🟢 Online"
    elif online == False:
        footer = f"🔴 Last online {last_visit_utc10_formatted}"
    else:
        footer = "Cannot fetch status"    
    icon = "https://cdn.britannica.com/78/6078-004-77AF7322/Flag-Australia.jpg"
    playtime = round(user.statistics.play_time / 3600)
    
    embed=discord.Embed(title="osu!", description="Bancho", color=0xece509)
    embed.set_author(name=username, url=link, icon_url=icon)
    embed.set_thumbnail(url=avatar)
    embed.add_field(name="Country", value=f"#{crank}", inline=True)
    embed.add_field(name="Global", value=f"#{grank}", inline=True)
    embed.add_field(name="Level", value=level, inline=True)
    embed.add_field(name="PP", value=pp, inline=True)
    embed.add_field(name="Accuracy", value=f"{acc}%", inline=True)
    embed.add_field(name="Playtime", value=f"{playtime} hours", inline=True)
    embed.set_footer(text=footer)
    await ctx.send(embed=embed)

server = JavaServer("49.190.201.61", 25565)

@client.command(aliases=["server", "serv"])
async def serverinfo(ctx):
    try:
        status = server.status()
        ip = "49.190.201.61:25565"
        motd = status.description
        version = status.version.name
        onlineplayers = status.players.online
        maxplayers = status.players.max
        playercount = f"{onlineplayers}/{maxplayers}"
        latency = round(server.ping())

        if status.players.sample:
            players = ', '.join(p.name for p in status.players.sample)
        else:
            players = ''

        #query = server.query()
        #players = query.players.names
        #software = query.software
        #map1 = query.map

        embed=discord.Embed(title="Online", color=0x0de711)
        embed.set_author(name="Server Status")
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/742686837612609599/1182197507464368178/image.png?ex=6583d239&is=65715d39&hm=37d76cd2e3682aed1dc26376e9b4a99999c1fcc171d49372195ac04f8d691d36&")
        embed.add_field(name="motd", value=motd, inline=True)
        embed.add_field(name="version", value=version, inline=True)
        embed.add_field(name="online players", value=playercount, inline=True)
        embed.add_field(name="ping", value=latency, inline=True)
        embed.add_field(name="player list", value=players, inline=True)
        #embed.add_field(name="software", value=software, inline=True)
        #embed.add_field(name="map", value=map1, inline=True)
        embed.set_footer(text=ip)
        await ctx.send(embed=embed)
    except:
        ip = "49.190.201.61:25565"
        embed=discord.Embed(title="Offline", color=0xed0c0c)
        embed.set_author(name="Server Status")
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/742686837612609599/1182197507464368178/image.png?ex=6583d239&is=65715d39&hm=37d76cd2e3682aed1dc26376e9b4a99999c1fcc171d49372195ac04f8d691d36&")
        embed.set_footer(text=ip)
        await ctx.send(embed=embed)
        await ctx.send("<:NOOO:990849108392697876>")

# admin trolling
@client.command()
@commands.is_owner()
async def snoof(ctx, member: discord.Member, *, reason=None):
    await member.kick(reason=reason)
    await ctx.send(f'{member} was snoofed')

@client.command()
@commands.has_permissions(kick_members=True)
async def minick(ctx, *, reason=None):
    member = ctx.guild.get_member(682776622176534651)   
    if member:
        await member.kick(reason=reason)
        await ctx.send(f'{member} was minicked')
    else:
        await ctx.send("Unable to find the target user.")

@client.command()
@commands.is_owner()
async def reload(ctx, extension):
    try:
        await client.reload_extension(f"cogs.{extension}")
        await ctx.send("done")
    except commands.ExtensionNotFound:
        await ctx.send("Extension not found.")
    except commands.ExtensionNotLoaded:
        await ctx.send("Extension is not loaded.")

@client.command()
@commands.is_owner()
async def shutdown(ctx):
    try:
        await client.close() 
        print("Shutdown successful.")
    except Exception as e:
        print(f"An error occurred during shutdown: {e}")
        client.clear()

@client.command()
async def help(ctx):
    embed = discord.Embed(title="Bot Commands", description="Here are the available commands:", color=discord.Color.blue())   
    # Add categories with emojis
    embed.add_field(name=":game_die: Events", value="tetrisinfo, toggle", inline=False)
    embed.add_field(name=":video_game: Gacha", value="roll, claims")
    embed.add_field(name=":bed: Hypickle", value="bedwarsstats, playerinfo", inline=False)
    embed.add_field(name=":musical_note: Music", value="add, disconnect, join, pause, play, queue, remove, repeat, resume, skip, stop, volume", inline=False)
    embed.add_field(name=":rocket: Phoenix 2", value="ship, ships", inline=False)
    embed.add_field(name=":grey_question: Misc", value="help, minick, serverinfo, wang", inline=False)
    
    # Add the Jim Game category
    embed.add_field(name=":video_game: Jim Game", value="game, score, leaderboard", inline=False)

    await ctx.send(embed=embed)

# Ensure the data folder exists
if not os.path.exists("./cogs/data"):
    os.mkdir("./cogs/data")

# Getting token from config.json file, .gitignore 
with open("config.json") as f:
    config = json.load(f)
    token = config["token"]

# bot token
if __name__ == "__main__":
    client.run(token)




















    
