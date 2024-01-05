import asyncio
import discord
from discord.ext import commands
import hypixel


class Hypickle(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(name="playerinfo", aliases=['pinfo', 'pi'])
    async def player_info(self, ctx, player_name):

        API_KEY = "ee270d2e-e8a8-4248-947f-5c8843163211" 
        # Initialize the Hypixel client
        hypixel_client = hypixel.Client(API_KEY)

        try:
            # Get player info using the Hypixel API
            async with hypixel_client:
                player = await hypixel_client.player(player_name)

            # Display player info in Discord
            embed = discord.Embed(title=f'Player Info for {player_name}', color=discord.Color.blue())
            embed.add_field(name='UUID', value=player.uuid)
            embed.add_field(name='Display Name', value=player.name)
            embed.add_field(name='Rank', value=player.rank)
            embed.add_field(name='First Login', value=player.first_login.strftime('%Y-%m-%d %H:%M:%S'))
            embed.add_field(name='Last Login', value=player.last_login.strftime('%Y-%m-%d %H:%M:%S') if player.last_login else 'Unknown')
            embed.add_field(name='Karma', value=player.karma)
            embed.add_field(name='Network Level', value=player.level)
            embed.add_field(name='Achievement Points', value=player.achievement_points)
            embed.set_thumbnail(url=f'https://crafatar.com/avatars/{player.uuid}')

            await ctx.send(embed=embed)
        except hypixel.PlayerNotFound:
            await ctx.send("Cannot find player")
        except hypixel.HypixelException as error:
            await ctx.send(f"An error occurred: {error}")

    @commands.command(name="bedwarsstats", aliases=['bws'])
    async def bedwars_stats(self, ctx, player_name):

        API_KEY = "ee270d2e-e8a8-4248-947f-5c8843163211" 
        # Initialize the Hypixel client
        hypixel_client = hypixel.Client(API_KEY)

        try:
            # Get player info using the Hypixel API
            async with hypixel_client:
                player = await hypixel_client.player(player_name)

            if not player.bedwars:
                await ctx.send("Bedwars stats not available for this player.")
                return

            # Extract Bedwars stats from the player object
            bedwars_stats = player.bedwars

            # Create an embed to display the stats
            embed = discord.Embed(title=f'Bedwars Stats for {player.name}', color=discord.Color.blue())
            embed.add_field(name='Coins', value=bedwars_stats.coins, inline=True)
            embed.add_field(name='Games Played', value=bedwars_stats.games, inline=True)
            embed.add_field(name='Wins', value=bedwars_stats.wins, inline=True)
            embed.add_field(name='Losses', value=bedwars_stats.losses, inline=True)
            embed.add_field(name='Win Rate', value=bedwars_stats.wlr, inline=True)
            embed.add_field(name='Kills', value=bedwars_stats.kills, inline=True)
            embed.add_field(name='Deaths', value=bedwars_stats.deaths, inline=True)
            embed.add_field(name='KDR', value=bedwars_stats.kdr, inline=True)
            embed.add_field(name='FKDR', value=bedwars_stats.fkdr, inline=True)
            embed.add_field(name='Level', value=bedwars_stats.level, inline=True)
            embed.set_thumbnail(url=f'https://crafatar.com/avatars/{player.uuid}')

            await ctx.send(embed=embed)
        except hypixel.PlayerNotFound:
            await ctx.send("Cannot find player")
        except hypixel.HypixelException as error:
            await ctx.send(f"An error occurred: {error}")

async def setup(client):
    await client.add_cog(Hypickle(client))
