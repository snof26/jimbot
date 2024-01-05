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

    # for toggling the brown event on and off
    @commands.command(name="toggle")
    async def toggle(self, ctx):
        self.Toggle = not self.Toggle
        await ctx.send("trolled")   

    # need to move this to another cog
    @commands.command(name="tetrisinfo", aliases=["tinfo", "ti"])
    async def tetrisinfo(self, ctx, userName):

        async def userData(user):
            async with aiohttp.ClientSession() as session:
                user = user.lower()
                URL = 'https://ch.tetr.io/api/users/' + user
                request = await session.get(URL)
                json = await request.json()
            return json

        async def userRecord(user):
            async with aiohttp.ClientSession() as session:
                user = user.lower()
                URL = 'https://ch.tetr.io/api/users/' + user + "/records"
                request = await session.get(URL)
                json = await request.json()
            return json

        def rank(rank):
            if (rank == "x"):
                return "<:rankX:845092185052413952>"
            elif (rank == "u"):
                return "<:rankU:845092171438882866>"
            elif (rank == "ss"):
                return "<:rankSS:845092157139976192>"
            elif (rank == "s+"):
                return "<:rankSplus:845092140471418900>"
            elif (rank == "s"):
                return "<:rankS:845092120662376478>"
            elif (rank == "s-"):
                return "<:rankSminus:845092009101230080>"
            elif (rank == "a+"):
                return "<:rankAplus:845091973248581672>"
            elif (rank == "a"):
                return "<:rankA:845091931994587166>"
            elif (rank == "a-"):
                return "<:rankAminus:845091885286424596>"
            elif (rank == "b+"):
                return "<:rankBplus:845091818911301634>"
            elif (rank == "b"):
                return "<:rankB:845089923089825812>"
            elif (rank == "b-"):
                return "<:rankBminus:845089882698154044>"
            elif (rank == "c+"):
                return "<:rankCplus:845088318509285416>"
            elif (rank == "c"):
                return "<:rankC:845088262611533844>"
            elif (rank == "c-"):
                return "<:rankCminus:845088252322775041>"
            elif (rank == "d+"):
                return "<:rankD:845088198966640640>"
            elif (rank == "d"):
                return "<:rankDplus:845088230588284959>"
            elif (rank == "z"):
                return "<:unranked:845092197346443284>"


        def badgesfunc(json):
            badgeEmojis = []
            badges = ""
            for i in range(len(json)):
                badgeEmojis.append(json[i]['id'])

            for x in range(len(badgeEmojis)):
                if ("leaderboard1" == badgeEmojis[x]):
                    badges += "<:zRank1:847188809907961886>"
                elif ("infdev" == badgeEmojis[x]):
                    badges += "<:zINF:847189521899454505>"
                elif ("allclear" == badgeEmojis[x]):
                    badges += "<:zPC:847188524247285771>"
                elif ("kod_founder" == badgeEmojis[x]):
                    badges += "<:zKOD:847188743680557146>"
                elif ("secretgrade" == badgeEmojis[x]):
                    badges += "<:zSG:847188855865868338>"
                elif ("20tsd" == badgeEmojis[x]):
                    badges += "<:z20tsd:1138082628889751583>"
                elif ("superlobby" == badgeEmojis[x]):
                    badges += "<:zHDSL:847190320986325034>"
                elif ("early-supporter" == badgeEmojis[x]):
                    badges += "<:zES:847188570769850380>"
                elif ("100player" == badgeEmojis[x]):
                    badges += "<:zSL:847188404163837953>"

            return badges

        user_data = await userData(userName)
        user_record = await userRecord(userName)

        userURL = "https://ch.tetr.io/u/" + userName

        user = user_data['data']['user']
        sprint = user_record['data']['records']['40l']['record']
        blitz = user_record['data']['records']['blitz']['record']
        emojiFlags = user['country']

        joinDate = datetime.datetime.strptime(
            user['ts'], "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%Y-%m-%d")

        playTime = round(user["gametime"]/3600, 2)

        # check if user exists
        if ("error" in user_data):
            embed_error = discord.Embed(
                title='No such user!', color=discord.Color.green())
            await msg.send(embed=embed_error)
            return

        # if the user has avatar 
        avatarURL = "https://tetr.io/res/avatar.png"
        if ("avatar_revision" in user):
            avatarURL = f"https://tetr.io/user-content/avatars/{user['_id']}.jpg?rv={user['avatar_revision']}"

        if (user['league']['gamesplayed'] > 10):
            currRank = rank(user['league']['rank'])
            # rating has been rounded up
            currRating = user['league']['rating']
            standing = user['league']['standing']
            standingLocal = user['league']['standing_local']
            pps = user['league']['pps']
            apm = user['league']['apm']
            vs = user['league']['vs']
            gpm = user['league']['vs'] * 0.6 - user['league']['apm']
        else:
            currRank = user['league']['rank'].upper()
            currRating = '-'
            standing = '-'
            standingLocal = '-'
            pps = '-'
            apm = '-'
            vs = '-'
            gpm = '-'

        if (blitz != None):
            blitz = f"{blitz['endcontext']['score']:,}"

        if (sprint == None):
            sprint = "None"
        else:
            sprint = sprint['endcontext']['finalTime']
            sprint = sprint / 1000
            m, s = divmod(sprint, 60)
            if (m > 0):
                sprint = f"{int(m)}:{s:.3f}"
            else:
                sprint = f"{s:.3f}"

        if (emojiFlags != None):
            emojiFlags = f":flag_{user['country'].lower()}:"
        else:
            emojiFlags = ":pirate_flag:"

        globeEmoji = ":globe_with_meridians:"
        userEmoji = emojiFlags + " " + userName.upper()
        badges = ""

        # check support, verified, and badges
        if ('verified' in user):
            if (user['verified'] == True):
                userEmoji += " <:verified:845092546979299328>"
        if ('supporter' in user):
            if (user['supporter'] == True):
                for i in range(user['supporter_tier']):
                    userEmoji += " <:support:845092535206674501>"
        if (len(user['badges']) != 0):
            badges = badgesfunc(user['badges'])

        embed = discord.Embed(title=userEmoji,
                            color=discord.Color.green(),
                            url=userURL)
        embed.set_author(name="Tetr.io",
                        icon_url="https://cdn.discordapp.com/emojis/676945644014927893.png?v=1")
        embed.set_thumbnail(url=avatarURL)
        embed.add_field(name="Tetra League",
                        value=f"{currRank} ({int(currRating)} TR) with {globeEmoji} {standing} / {emojiFlags} {standingLocal}",
                        inline=False)
        embed.add_field(name="Stats",
                        value=f"_**PPS**_ {pps:.2f}\n_**APM**_ {apm:.2f}\n_**VS**_ {vs:.2f}\n_**GPM**_ {gpm:.2f}",
                        inline=True)
        embed.add_field(name="Solo Records",
                        value=f"_**Sprint(40L)**_ {sprint}\n_**Blitz**_ {blitz}\n{badges}",
                        inline=True)
        embed.add_field(name="Date Joined",
                        value=joinDate,
                        inline=True)
        embed.add_field(name="Hours Played",
                        value=playTime,
                        inline=True)

        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_presence_update(self, before, after):
        member = self.client.get_user(447651478941728768) # fauntts user id
        now = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=10)  # AEST is UTC+10

        # Check if it is outside of school hours (after 3:20 pm AEST or before 8:48 am AEST)
        if (
            ((now.hour > 15 or (now.hour == 15 and now.minute >= 20)) or (now.hour < 8 or (now.hour == 8 and now.minute <= 48)))
            and now.weekday() not in (5, 6)  # Saturday and Sunday are 5 and 6 respectively
        ):
            # Check if TETR.IO playing status was not logged previously
            if after.activity and after.activity.name == "TETR.IO" and not self.tetrio_logged:
                self.playing_tetrio_counter += 1
                self.tetrio_logged = True
            elif not after.activity or after.activity.name != "TETR.IO":
                # Reset the flag when TETR.IO playing status stops
                self.tetrio_logged = False

    # main events
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.client.user:
            return

        # says "your mother" if person asks a question
        if message.content.endswith("?"):
	        p = random.randint(0,10)
	        if p == 6:
		        await message.channel.send("your mother")
	        else:
		        pass		
        
        # says "kill yourself" if person tries to imitate jim
        if message.content.endswith("askers"):
            l = random.randint(0, 2)
            if l == 1:
                await message.channel.send("kill yourself")
            else:
                await message.channel.send("snoof yourself")

        # says "no u" if person tries to imitate jim
        if message.content.endswith("kys") or message.content.endswith("kill yourself"):
            k = random.randint(0, 2)
            if k == 1:
                await message.channel.send("no u")
            else:
                await message.channel.send("the snoofing")

        # says "askers" if person tries to apologise to jim
        if message.content.startswith("mb") or message.content.startswith("my bad") or message.content.startswith("sorry"):
            n = random.randint(0, 2)
            if n == 1:
                await message.channel.send("askers") 
            else:
                await message.channel.send("inquirers")
        # says "askers" if person sends an attachment
        def has_file(message):
            return len(message.attachments) > 0
        
        if has_file(message) == True:
            p = random.randint(0, 5)
            if p == 1:
                n = random.randint(0, 2)
                if n == 1:
                    await message.channel.send("askers") 
                else:
                    await message.channel.send("inquirers")
            else:
                pass
        else:
            pass

        # sends clash royale laughing gif if person says "fuck you" or "fuck off or other variations"
        if message.content.endswith("fuck you") or message.content.endswith("fuck off") or message.content.endswith("fuck u"):
            n = random.randint(0, 2)
            if n == 1:
                await message.channel.send("quite humorous") 
            else:
                await message.channel.send("https://tenor.com/view/clash-royale-emotes-laugh-smile-king-gif-14309345")

        if message.content.lower() == "minicide":
        # Check if the message author is not a bot
            if not message.author.bot:
                # Check if the bot has the necessary permissions
                if message.guild.me.guild_permissions.moderate_members:
                    # Calculate the timeout duration (1 hour)
                    timeout_duration = datetime.timedelta(hours=1)

                    # Calculate the timeout expiry time
                    timeout_expiry = datetime.datetime.utcnow() + timeout_duration

                    # Timeout the member until the expiry time
                    await message.author.timeout(timeout_expiry, reason="Timeout for saying 'minicide'")
                    await message.channel.send(f"shut up {message.author}")
        
        # 0.1% chance of brown (if snoof or kxnai or tanmay or daniel abdz send a message)
        if self.Toggle: 
            if message.author.id == 333163516695412736 or message.author.id == 495897505469562880 or message.author.id == 441853903005417482 or message.author.id == 587561428848738305: #snoof user id and kxnai user id and daniel abdz and snoof alt user id
                n = random.randint(0, 100)
                if n == 5:
                    await message.channel.send("brown :index_pointing_at_the_viewer:")
                else:
                    pass
        else:
            pass

        # 0.001% chance of random uncommon jim phrase
        lines = open("./phrases.txt").read().splitlines() # /home/pi/Desktop/jimbot/phrases.txt
        myline = random.choice(lines)

        if message:
            n = random.randint(0, 1000)
            if n == 69:
                await message.channel.send(myline)
    
async def setup(client):
    await client.add_cog(Events(client))
