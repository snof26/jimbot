import discord
from discord.ext import commands
import random
import openpyxl as op
import asyncio
import datetime
import json


class Gacha(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.image_data = op.load_workbook("./images.xlsx")  # Load data within __init__
        self.claims = {}
        self.load_claims()

    @classmethod
    def get_rarity(cls, roll_value): 
        # Determines the rarity of a roll based on the provided brackets.

        if 1 <= roll_value <= 600:
            return "Common"
        elif 601 <= roll_value <= 750:
            return "Rare"
        elif 751 <= roll_value <= 875:
            return "Epic"
        elif 876 <= roll_value <= 975:
            return "Minickal"
        elif 976 <= roll_value <= 1000:
            return "LeJIMdary"
        else:
            raise ValueError("Roll value must be between 1 and 1000.")

    @classmethod
    def update_embed_footer(cls, embed, user):
        # Update the embed's footer with the user who claimed the image
        embed.set_footer(text=f"Claimed by {user.display_name}", icon_url=user.avatar.url)
        return embed

    # Functions for loading and saving claims
    def load_claims(self):
        try:
            with open("claims.json", "r") as f:
                loaded_claims = json.load(f)
                # Convert keys (guild IDs) back to integers
                self.claims = {int(guild_id): claim_data for guild_id, claim_data in loaded_claims.items()}
        except FileNotFoundError:
            self.claims = {}

    def save_claims(self):
        # Convert keys (guild IDs) to strings before saving
        claims_to_save = {str(guild_id): claim_data for guild_id, claim_data in self.claims.items()}
        with open("claims.json", "w") as f:
            json.dump(claims_to_save, f, indent=4)

    @commands.command(name="roll", aliases=["r"])
    #@commands.cooldown(1, 3600, commands.BucketType.user)
    async def roll(self, ctx):
        try:
            rv = random.randint(1, 1000)
            rarity = self.get_rarity(rv)
            print(rarity)

            # Filter image data based on rarity
            relevant_images = self.image_data.active

            matching_images = [image for image in relevant_images.iter_rows(min_row=2, values_only=True)
                                if image[2] == rarity]  # Assuming "Rarity" is in the third column (column C)

            if not matching_images:
                await ctx.send("There are no matching images for this rarity.")
                return

            random_image = random.choice(matching_images)
            image_name = random_image[1]  # Assuming "Name" is in the second column (column B)
            image_url = random_image[0]  # Assuming "Image URL" is in the first column (column A)

            if image_name not in self.claims.get(ctx.guild.id, {}):
                # Send embed and start claim timer
                embed = discord.Embed(
                    title=image_name,
                    color=discord.Color.green(),
                    timestamp=datetime.datetime.now(datetime.timezone.utc)
                )
                embed.set_image(url=image_url)
                embed.add_field(name="Rarity", value=rarity)
                message = await ctx.send(embed=embed)

                try:
                    await asyncio.sleep(30)  # Wait for 30 seconds for claims
                    if image_name not in self.claims.get(ctx.guild.id, {}):
                        # Remove claim if not reacted to
                        self.claims.setdefault(ctx.guild.id, {}).pop(image_name, None)
                except asyncio.CancelledError:
                    pass  # Ignore cancellation if the message is edited or deleted
                self.save_claims()
            else:
                claimed_by_user_id = self.claims.get(ctx.guild.id, {}).get(image_name)
                claimed_by_user = await self.client.fetch_user(int(claimed_by_user_id))

                # Check if the user trying to roll is the one who claimed the image
                if claimed_by_user_id == str(ctx.author.id):
                    await ctx.send(f"You cannot claim {image_name} again. It's already claimed by you.")
                else:
                    # Send the image with a claimed footer
                    embed = discord.Embed(
                        title=image_name,
                        color=discord.Color.green(),
                        timestamp=datetime.datetime.now(datetime.timezone.utc)
                    )
                    embed.set_image(url=image_url)
                    embed.add_field(name="Rarity", value=rarity)
                    embed.set_footer(text=f"Claimed by {claimed_by_user.display_name}", icon_url=claimed_by_user.avatar.url)
                    await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"An error occurred: {str(e)}")

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            remaining_time_minutes = round(error.retry_after / 60, 2)
            await ctx.send(f"Command on cooldown. Please wait {remaining_time_minutes} minutes before trying again.")

    # Call save_claims before closing
    @commands.Cog.listener()
    async def on_ready(self):
        self.client.loop.create_task(self.save_claims_on_close())

    async def save_claims_on_close(self):
        await self.client.wait_for("close")
        self.save_claims()  # Save claims before closing

    @commands.command(name="claims")
    async def view_claims(self, ctx):
        # Retrieve and filter claims for the current user (using string comparisons)
        author_id_str = str(ctx.author.id)
        user_claims = {
            image_name: user_id
            for image_name, user_id in self.claims.get(ctx.guild.id, {}).items()
            if user_id == author_id_str  # Compare with string outside the loop
        }
        print(user_claims)
        print(self.claims)
        print(str(ctx.author.id))
        if user_claims:
            claim_list = "\n".join(f"**{image_name}**" for image_name in user_claims)
            await ctx.send(f"Here are your claims:\n{claim_list}")
        else:
            await ctx.send("You haven't claimed any jims yet.")


    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        # Verify reaction on embed and within claim period
        if reaction.message.embeds and user != self.client.user and reaction.message.channel.permissions_for(user).add_reactions:
            embed = reaction.message.embeds[0]

            # Check for embed.timestamp and footer conditions
            if embed.timestamp and (not embed.footer or ("Claimed by" not in embed.footer.text if embed.footer.text else True)):
                time_difference = datetime.datetime.now(datetime.timezone.utc) - embed.timestamp
                if time_difference < datetime.timedelta(seconds=30):
                    image_name = embed.title

                    # Initialize an empty list if the image key doesn't exist
                    self.claims.setdefault(reaction.message.guild.id, {}).setdefault(image_name, [])

                    # Check if the user has already claimed the image
                    if str(user.id) not in self.claims[reaction.message.guild.id][image_name]:
                        # Update claims (store single user ID)
                        self.claims[reaction.message.guild.id][image_name] = str(user.id)
                        self.save_claims()

                        # Update embed footer and notify
                        await reaction.message.edit(embed=self.update_embed_footer(embed, user))
                        await reaction.message.channel.send(f"{image_name} has been claimed by {user.mention}!")

    @commands.command(name="rarity")
    async def rarelist(self, ctx):
        embed=discord.Embed(title="Rarity Levels", description="Rarities of Jim Gacha", color=0x000000)
        embed.add_field(name="Common", value=":green_circle:", inline=False)
        embed.add_field(name="Rare", value=":blue_circle:", inline=False)
        embed.add_field(name="Epic", value=":purple_circle: ", inline=False)
        embed.add_field(name="Minickal", value=":red_circle:", inline=False)
        embed.add_field(name="LeJIMdary", value=":orange_circle:", inline=False)
        embed.set_footer(text="big peen")
        await ctx.send(embed=embed)

async def setup(client):
    await client.add_cog(Gacha(client))
