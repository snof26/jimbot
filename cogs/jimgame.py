import discord
from discord.ext import commands
import random
import asyncio
import json
import os

class JimGame(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.user_points = {}  # Dictionary to store user points

    async def save_points(self, guild_id):

        script_directory = os.path.dirname(os.path.abspath(__file__))        
        data_directory = os.path.join(script_directory, "data")
        file_path = os.path.join(data_directory, f"{guild_id}_points.json")
        
        print("File path:", file_path)
        try:
            with open(file_path, "w") as f:
                json.dump(self.user_points, f)
            print(f"Points saved for guild {guild_id}")
        except Exception as e:
            print(f"Error saving points for guild {guild_id}: {e}")

    async def load_points(self, guild_id):

        script_directory = os.path.dirname(os.path.abspath(__file__))        
        data_directory = os.path.join(script_directory, "data")
        file_path = os.path.join(data_directory, f"{guild_id}_points.json")

        print("Loading points from:", file_path)
        try:
            with open(file_path, "r") as f:
                self.user_points = json.load(f)
            print(f"Points loaded for guild {guild_id}")
        except Exception as e:
            print(f"Error loading points for guild {guild_id}: {e}")

    @commands.command(name="game")
    async def startgame(self, ctx):
        phrases = [
            "ban ben bin",
            "ban ben bon",
            "ban bin ben",
            "ban bin bon",
            "ban bon ben",
            "ban bon bin",
            "ben ban bin",
            "ben ban bon",
            "ben bin ban",
            "ben bin bon",
            "ben bon ban",
            "ben bon bin",
            "bin ban ben",
            "bin ban bon",
            "bin ben ban",
            "bin ben bon",
            "bin bon ban",
            "bin bon ben",
            "bon ban ben",
            "bon ban bin",
            "bon ben ban",
            "bon ben bin",
            "bon bin ban",
            "bon bin ben"
        ]
        correct_phrase = random.choice(phrases)
        await ctx.send("A three-word phrase has been selected! Guess the correct order of words.")
        await ctx.send("Here are the words: bin, ben, ban, bon")

        def check(message):
            return message.author == ctx.author and message.channel == ctx.channel

        try:
            user_response = await self.client.wait_for('message', timeout=30.0, check=check)
        except asyncio.TimeoutError:
            await ctx.send("Time's up! The correct phrase was: " + correct_phrase)
        else:
            user_guess = user_response.content.lower()
            if user_guess == correct_phrase:
                # Update user points
                username_key = ctx.author.name
                if username_key not in self.user_points:
                    self.user_points[username_key] = 1
                else:
                    self.user_points[username_key] += 1
                await ctx.send(f"Congratulations {ctx.author.mention}! You guessed it correctly. Your points: {self.user_points[username_key]}")
                await self.save_points(ctx.guild.id)  # Save points after update
            else:
                await ctx.send(f"Sorry {ctx.author.mention}, that's incorrect. The correct phrase was: " + correct_phrase)

    @commands.command(name="score")
    async def myscore(self, ctx):
        username_key = ctx.author.name
        if username_key in self.user_points:
            points = self.user_points[username_key]
            await ctx.send(f"{ctx.author.mention}, Your current score is: {points}")
        else:
            await ctx.send(f"{ctx.author.mention}, you haven't participated in any games yet.")

    @commands.command(name="leaderboard", aliases=["lb"])
    async def leaderboard(self, ctx):
        if not self.user_points:
            await ctx.send("No user scores available.")
            return

        sorted_users = sorted(self.user_points.items(), key=lambda item: item[1], reverse=True)

        leaderboard_text = "Leaderboard:\n"
        for index, (username_key, points) in enumerate(sorted_users, start=1):
            leaderboard_text += f"{index}. {username_key}: {points} points\n"

        await ctx.send(leaderboard_text)

    @commands.command(name="resetleaderboard", aliases=["rlb"])
    @commands.is_owner()
    async def reset_leaderboard(self, ctx):
        # Reset the leaderboard for this server
        confirmation = await ctx.send("Are you sure you want to reset the leaderboard? (y/n)")
        try:
            response = await self.client.wait_for('message', timeout=15.0, check=lambda message: message.author == ctx.author and message.channel == ctx.channel)
        except asyncio.TimeoutError:
            await ctx.send("No response received. Leaderboard reset cancelled.")
        else:
            if response.content.lower() == "y":
                self.user_points = {}
                await ctx.send("Leaderboard reset")
                await self.save_points(ctx.guild.id)
            elif response.content.lower() == "n":
                await ctx.send("Leaderboard reset cancelled")
            else:
                await ctx.send("No response received. Leaderboard reset cancelled.")

async def setup(client):
    cog = JimGame(client)
    await client.add_cog(cog)
    
    # Load points for each guild
    for guild in client.guilds:
        await cog.load_points(guild.id)