import discord
from discord.ext import commands
import random
import datetime
import aiohttp

class Events(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.Toggle = True

    @commands.command(name="toggle")
    async def toggle(self, ctx):
        self.Toggle = not self.Toggle
        await ctx.send("Toggled the brown event.")

async def setup(client):
    await client.add_cog(Events(client))
