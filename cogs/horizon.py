import discord
from discord.ext import commands
import datetime
from dependencies import sun  # Adjust this import based on your project structure

class Horizon(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def sunrise(self, ctx, location, *, date=None):
        weather_api_key = '60d55d74511ed95d2ec07c44b354f209'  # Your OpenWeatherMap API key

        # Determine the date to use
        if date == "tomorrow":
            date_to_use = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
        elif not date:
            date_to_use = None
        else:
            try:
                date_to_use = datetime.datetime.strptime(date, '%Y-%m-%d').strftime('%Y-%m-%d')
            except ValueError:
                await ctx.send("Invalid date format. Please use YYYY-MM-DD or 'tomorrow'.")
                return

        # Get the sunrise quality
        try:
            sunrise_quality, _ = sun.predict_sunrise_sunset_quality(location, weather_api_key, date_to_use)
            date_str = date_to_use if date_to_use else 'today'
            await ctx.send(f"Predicted sunrise quality rating for {location} on {date_str} is: {sunrise_quality}")
        except ValueError as e:
            await ctx.send(str(e))

    @commands.command()
    async def sunset(self, ctx, location, *, date=None):
        weather_api_key = '60d55d74511ed95d2ec07c44b354f209'  # Your OpenWeatherMap API key

        # Determine the date to use
        if date == "tomorrow":
            date_to_use = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
        elif not date:
            date_to_use = None
        else:
            try:
                date_to_use = datetime.datetime.strptime(date, '%Y-%m-%d').strftime('%Y-%m-%d')
            except ValueError:
                await ctx.send("Invalid date format. Please use YYYY-MM-DD or 'tomorrow'.")
                return

        # Get the sunset quality
        try:
            _, sunset_quality = sun.predict_sunrise_sunset_quality(location, weather_api_key, date_to_use)
            date_str = date_to_use if date_to_use else 'today'
            await ctx.send(f"Predicted sunset quality rating for {location} on {date_str} is: {sunset_quality}")
        except ValueError as e:
            await ctx.send(str(e))

async def setup(client):
    await client.add_cog(Horizon(client))
