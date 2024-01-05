import discord
from discord.ext import commands
import wavelink
import asyncio

class Music(commands.Cog):
    vc: wavelink.Player = None
    current_track = None
    queue = None
    disconnect_timer = None
    repeat = False

    def __init__(self, client):
        self.client = client
        self.queue = asyncio.Queue()

    async def setup(self):
        node: wavelink.Node = wavelink.Node(uri='http://localhost:2333', password='youshallnotpass')
        await wavelink.NodePool.connect(client=self.client, nodes=[node])

    def start_disconnect_timer(self):
        self.disconnect_timer = self.client.loop.call_later(600, self.disconnect_after_timeout)

    def cancel_disconnect_timer(self):
        if self.disconnect_timer and not self.disconnect_timer.cancelled():
            self.disconnect_timer.cancel()

    async def disconnect_after_timeout(self):
        await self.vc.disconnect()
        self.vc = None
        self.current_track = None
        while not self.queue.empty():
            await self.queue.get()  # Clear the queue

    @commands.Cog.listener()
    async def on_wavelink_node_ready(self, node: wavelink.Node):
        print(f"{node} is ready")

    @commands.Cog.listener()
    async def on_wavelink_track_end(self, payload: wavelink.TrackEventPayload):
        if payload.reason == 'FINISHED':
            if self.repeat:
                await payload.player.play(self.current_track)  # Repeat the current track
            elif not self.queue.empty():
                next_track = await self.queue.get()
                await payload.player.play(next_track)
                self.start_disconnect_timer()  # Start the disconnect timer after playing the next track
            else:
                self.cancel_disconnect_timer()  # Cancel the disconnect timer if the queue is empty

    @commands.command(name="join")
    async def join(self, ctx):
        channel = ctx.message.author.voice.channel
        if channel:
            self.vc = await channel.connect(cls=wavelink.Player)
            await ctx.send(f"Joined `{channel.name}`")
        else:
            await ctx.send("You are not connected to a voice channel.")

    @commands.command(name="add")
    async def add(self, ctx, *, title: str):
        tracks = await wavelink.YouTubeTrack.search(title)
        if tracks:
            chosen_track = tracks[0]
            self.current_track = chosen_track
            if self.vc:
                await self.queue.put(chosen_track)
                await ctx.send(f"Added `{self.current_track}` to the queue")
                print(self.queue)
            else:
                await ctx.send("Please use the `join` command first to join a voice channel.")

    @commands.command(name="play")
    async def play(self, ctx):
        if self.current_track and self.vc:
            if not self.vc.is_playing():
                track = await self.queue.get()
                await self.vc.play(track)
                await ctx.send(f"Playing `{track}`")
            else:
                await ctx.send("The bot is already playing a track.")
        else:
            await ctx.send("No track is added or the bot is not connected to a voice channel.")

    @commands.command(name="pause")
    async def pause(self, ctx):
        await self.vc.pause()
    
    @commands.command(name="resume")
    async def resume(self, ctx):
        await self.vc.resume()

    @commands.command(name="stop")
    async def stop(self, ctx):
        await self.vc.stop()

    @commands.command(name="volume", aliases=["vol"])
    async def volume(self, ctx, new_volume: int = 100):
        if new_volume < 0 or new_volume > 100:
            await ctx.send("Please provide a volume value between 0 and 100.")
            return

        await self.vc.set_volume(new_volume)
        await ctx.send(f"Volume set to {new_volume}%")


    @commands.command(name="skip")
    async def skip(self, ctx):
        if self.vc:
            if not self.vc.is_playing():
                await ctx.send("No track is currently playing.")
                return

            if self.queue.empty():
                await ctx.send("The queue is empty.")
                return

            self.current_track = await self.queue.get()
            await self.vc.play(self.current_track)
            await ctx.send(f"Skipping to the next track: `{self.current_track}`")
        else:
            await ctx.send("The bot is not connected to a voice channel.")
    
    @commands.command(name="queue", aliases=["q"])
    async def queue(self, ctx):
        if self.queue.empty():
            await ctx.send("The queue is empty.")
            return

        track_list = list(self.queue._queue)
        queue_message = "Current Queue:\n"
        for index, track in enumerate(track_list, start=1):
            queue_message += f"{index}. `{track}`\n"

        await ctx.send(queue_message)

    @commands.command(name="remove")
    async def remove(self, ctx, position: int):
        if not self.queue.empty():
            queue_size = self.queue.qsize()
            if position < 1 or position > queue_size:
                await ctx.send(f"Invalid position. Please provide a value between 1 and {queue_size}.")
                return

            removed_tracks = []
            for _ in range(queue_size):
                track = await self.queue.get()
                if position != 1:
                    await self.queue.put(track)
                else:
                    removed_tracks.append(track)
                position -= 1

            if removed_tracks:
                removed_track_names = ", ".join([str(track) for track in removed_tracks])
                await ctx.send(f"Removed `{removed_track_names}` from the queue.")
            else:
                await ctx.send("No tracks were removed from the queue.")
        else:
            await ctx.send("The queue is empty.")

    @commands.command(name="disconnect", aliases=["dc"])
    async def disconnect(self, ctx):
        if self.vc and self.vc.is_connected():
            await self.vc.disconnect()
            self.vc = None
            self.current_track = None
            while not self.queue.empty():
                await self.queue.get()  # Clear the queue
            self.cancel_disconnect_timer()  # Cancel the disconnect timer
            await ctx.send("Disconnected from the voice channel and cleared the queue.")
        else:
            await ctx.send("The bot is not connected to a voice channel.")

    @commands.command(name="repeat", aliases=["loop"])
    async def repeat_song(self, ctx):
        self.repeat = not self.repeat
        if self.repeat:
            await ctx.send("Enabled song repeat.")
        else:
            await ctx.send("Disabled song repeat.")

async def setup(client):
    music_bot = Music(client)
    await client.add_cog(music_bot)
    await music_bot.setup()
