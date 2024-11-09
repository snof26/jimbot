import discord
from discord.ext import commands
import datetime
import aiohttp

class Tetrio(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.Toggle = True
        self.tetrio_logged = False

    @commands.command(name="tetrisinfo", aliases=["tinfo", "ti"])
    async def tetrisinfo(self, ctx, username):
        async with aiohttp.ClientSession() as session:
            headers = {
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                        }
            try:
                # Fetch user data
                user_url = f'https://ch.tetr.io/api/users/{username.lower()}'
                async with session.get(user_url, headers=headers) as user_response:
                    user_data = await user_response.json()
                    if user_response.status != 200 or not user_data.get("success", False):
                        await ctx.send("Failed to fetch user data from Tetrio. Please check the username.")
                        return

                # Extract user data if available
                user = user_data.get('data', {})
                if not user:
                    await ctx.send("Unable to extract user information from response.")
                    return

                # Extract user profile information
                user_id = user.get('_id', 'N/A')
                username = user.get('username', 'Unknown User')
                join_date_str = "Unknown"
                join_date = user.get('ts')
                if join_date:
                    try:
                        join_date_str = datetime.datetime.strptime(join_date, "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%Y-%m-%d")
                    except ValueError:
                        pass

                play_time = round(user.get("gametime", 0) / 3600, 2)
                games_played = user.get("gamesplayed", 0)
                games_won = user.get("gameswon", 0)
                country = user.get("country", "Unknown")

                # Avatar URL with a fallback to a default URL
                avatar_url = f"https://tetr.io/user-content/avatars/{user_id}.jpg?rv={user.get('avatar_revision', 0)}"

                # Extract badge information
                badges = user.get('badges', [])
                badge_list = self.badgesfunc(badges)

                # Extract rank information
                league = user.get('league', {})
                curr_rank = league.get('rank', "Unranked").upper() if league.get('gamesplayed', 0) > 10 else "Unranked"

                # Fetch user summaries (to get various game summaries)
                summaries_url = f'https://ch.tetr.io/api/users/{username.lower()}/summaries'
                async with session.get(summaries_url, headers=headers) as summaries_response:
                    summaries_data = await summaries_response.json()
                    if summaries_response.status != 200 or not summaries_data.get("success", False):
                        await ctx.send("Failed to fetch user summaries from Tetrio.")
                        return

                # Extract specific game mode summaries
                records = summaries_data.get('data', {})
                sprint_record = records.get('40l', {}).get('record', {})
                blitz_record = records.get('blitz', {}).get('record', {})

                sprint_time = sprint_record.get('results', {}).get('stats', {}).get('finaltime', "None")
                if sprint_time != "None":
                    sprint_time = f"{sprint_time / 1000:.2f} s"  # Convert ms to seconds

                blitz_score = blitz_record.get('results', {}).get('stats', {}).get('score', "None")
                if blitz_score != "None":
                    blitz_score = f"{blitz_score:,}"  # Format with commas

                # Fetch user Tetra League data
                league_url = f'https://ch.tetr.io/api/users/{username.lower()}/summaries/league'
                async with session.get(league_url, headers=headers) as league_response:
                    league_data = await league_response.json()
                    if league_response.status != 200 or not league_data.get("success", False):
                        await ctx.send("Failed to fetch Tetra League information from Tetrio.")
                        return

                # Extract league rank and stats
                league = league_data.get('data', {})
                best_rank = league.get('bestrank', 'N/A').upper()
                standing = league.get('standing', 'N/A')
                standing_local = league.get('standing_local', 'N/A')
                curr_rank = league.get('rank', "Unranked").upper() if league.get('gamesplayed', 0) >= 10 else "Unranked"
                glicko = league.get('glicko', -1)
                tr = league.get('tr', -1)
                gxe = league.get('gxe', -1)

                # Additional league stats if available
                games_played_league = league.get('gamesplayed', 0)
                games_won_league = league.get('gameswon', 0)
                winrate = round(((games_won_league/games_played_league)*100), 2)
                apm = league.get('apm', 'N/A')
                pps = league.get('pps', 'N/A')
                vs = league.get('vs', 'N/A')

                # Build the embed for displaying user information
                embed = discord.Embed(title=f"{username}", color=discord.Color.blue(), url=f"https://ch.tetr.io/u/{username}")
                embed.set_thumbnail(url=avatar_url)

                # General Stats

                embed.add_field(name="Joined", value=f"{join_date_str}", inline=True)
                embed.add_field(name="Country", value=f":flag_{country.lower()}:" if country != "Unknown" else "Unknown", inline=True)
                embed.add_field(name="Hours Played", value=f"{play_time} hours", inline=True)
                embed.add_field(name="Badges", value=badge_list or "None", inline=True)
                embed.add_field(name="40L", value=f"{sprint_time}", inline=True)
                embed.add_field(name="Blitz", value=f"{blitz_score}", inline=True)
                embed.add_field(name="\u200b", value="", inline=False)  # Blank line separator
                # Tetra League Stats
                embed.add_field(name="**TL Season Stats**", value="", inline=False)
                embed.add_field(name="Rank", value=f"{curr_rank}", inline=True)
                embed.add_field(name="Glicko", value=f"{glicko:.2f}" if glicko != -1 else "Unranked", inline=True)
                embed.add_field(name="TR", value=f"{tr:.2f}" if tr != -1 else "Unranked", inline=True)
                embed.add_field(name="Peak", value=f"{best_rank}", inline=True)
                embed.add_field(name="Global", value=f"{standing}", inline=True)
                embed.add_field(name="Country", value=f"{standing_local}", inline=True)
                embed.add_field(name="Games", value=f"{games_played_league}", inline=True)
                embed.add_field(name="Winrate", value=f"{winrate}%", inline=True)
                embed.add_field(name="APM", value=f"{apm}", inline=True)
                embed.add_field(name="PPS", value=f"{pps}", inline=True)
                embed.add_field(name="VS", value=f"{vs}", inline=True)
                embed.add_field(name="GXE", value=f"{gxe:.2f}%" if gxe != -1 else "Unranked", inline=True)

                embed.set_footer(text="TETR.IO CHANNEL", icon_url="https://pbs.twimg.com/profile_images/1286993509573169153/pN9ULwc6_400x400.jpg")

                await ctx.send(embed=embed)
            
            except Exception as e:
                await ctx.send(f"An error occurred: {e}")
                print(f"Unexpected error: {e}")

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
        # Return the concatenated list of badge icons
        return ''.join(badge_icons.get(badge['id'], "") for badge in badges)

async def setup(client):
    await client.add_cog(Tetrio(client))
