import discord
from discord.ext import commands
import random
import datetime
import aiohttp

class Events(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.Toggle = True
        self.tetrio_logged = False
        self.playing_tetrio_counter = 0

    @commands.command(name="toggle")
    async def toggle(self, ctx):
        self.Toggle = not self.Toggle
        await ctx.send("Toggled the brown event.")

    @commands.command(name="tetrisinfo", aliases=["tinfo", "ti"])
    async def tetrisinfo(self, ctx, username):
        async with aiohttp.ClientSession() as session:
            try:
                # Fetch user data
                user_url = f'https://ch.tetr.io/api/users/{username.lower()}'
                async with session.get(user_url) as user_response:
                    # Debugging: Log status and data
                    print(f"User data response status: {user_response.status}")
                    user_data = await user_response.json()
                    print(f"User data response content: {user_data}")
                    
                    if user_response.status != 200 or "error" in user_data:
                        await ctx.send("Failed to fetch user data from Tetrio. Please check the username.")
                        return

                # Fetch user records
                records_url = f'https://ch.tetr.io/api/users/{username.lower()}/records'
                async with session.get(records_url) as record_response:
                    print(f"Record data response status: {record_response.status}")
                    user_records = await record_response.json()
                    print(f"Record data response content: {user_records}")

                    if record_response.status != 200:
                        await ctx.send("Failed to fetch user records from Tetrio.")
                        return

                # Extract user data
                user = user_data['data']['user']
                avatar_url = f"https://tetr.io/user-content/avatars/{user['_id']}.jpg?rv={user.get('avatar_revision', 0)}"
                join_date = datetime.datetime.strptime(user['ts'], "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%Y-%m-%d")
                play_time = round(user["gametime"] / 3600, 2)

                # Extract sprint and blitz data
                sprint_time = user_records['data']['records']['40l']['record']['endcontext']['finalTime'] if '40l' in user_records['data']['records'] else "None"
                blitz_score = f"{user_records['data']['records']['blitz']['record']['endcontext']['score']:,}" if 'blitz' in user_records['data']['records'] else "None"

                # Define rank and badges
                curr_rank = user['league']['rank'].upper() if 'league' in user and user['league']['gamesplayed'] > 10 else "Unranked"
                badges = self.badgesfunc(user['badges']) if 'badges' in user else ""

                # Build the embed
                embed = discord.Embed(title=user['username'], color=discord.Color.green(), url=f"https://ch.tetr.io/u/{username}")
                embed.set_thumbnail(url=avatar_url)
                embed.add_field(name="Tetra League Rank", value=curr_rank, inline=True)
                embed.add_field(name="Sprint Record (40L)", value=sprint_time, inline=True)
                embed.add_field(name="Blitz Score", value=blitz_score, inline=True)
                embed.add_field(name="Date Joined", value=join_date, inline=True)
                embed.add_field(name="Hours Played", value=str(play_time), inline=True)
                embed.add_field(name="Badges", value=badges or "None", inline=True)

                await ctx.send(embed=embed)
            
            except Exception as e:
                await ctx.send(f"An error occurred: {e}")
                print(f"Exception occurred: {e}")

    def badgesfunc(self, badges):
        badge_icons = {
            "leaderboard1": "<:zRank1:1138082638326943805>",
            "infdev": "<:zINF:1138082645922807828>",
            "allclear": "<:zPC:1138082631880290344>",
            "kod_founder": "<:zKOD:1138082636905054228>",
            "secretgrade": "<:zSG:1138082642550599720>",
            "20tsd": "<:z20tsd:1138082628889751583>",
            "superlobby": "<:zHDSL:1138082648137400450>",
            "early-supporter": "<:zES:1138082633725780089>",
            "100player": "<:zSL:1138082626780020868>"
        }
        return ''.join(badge_icons.get(badge['id'], "") for badge in badges)

async def setup(client):
    await client.add_cog(Events(client))
