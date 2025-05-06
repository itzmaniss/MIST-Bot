from features.base import BotFeature
from utils.logger import Logger
from config.config import Config
from utils.cache import MusicCache
from utils.helpers import discord_message, discord_embed
import queue
import yt_dlp
import discord
import asyncio
import aiohttp
import re
from typing import List, Dict
from discord import app_commands


# un-comment for mac
# discord.opus.load_opus("/opt/homebrew/Cellar/opus/1.5.2/lib/libopus.0.dylib")


class MusicFeature(BotFeature):
    def __init__(self, bot):
        super().__init__(bot)

        # Basic configs
        self.ydl_opts = {
            "format": "bestaudio/best",
            "noplaylist": True,
            "quiet": True,
            "extract_flat": False,
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "wav",
                    "preferredquality": "320",
                }
            ],
        }

        self.playlist_opts = {
            "format": "bestaudio/best",
            "noplaylist": False,
            "quiet": True,
            "extract_flat": "in_playlist",
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "wav",
                    "preferredquality": "320",
                }
            ],
        }

        self.ffmpeg_opts = {
            "options": "-vn -b:a 192k",
            "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
        }
        self.config = Config()
        self.logger = Logger("Music Bot")
        self.cache = MusicCache()
        self.pending_playlist_tracks = []
        self.is_processing_playlist = False

        # Player state
        self.queue = queue.Queue()
        self.channel = None
        self.current_player = None
        self.volume = 1.0
        self.loop = False
        self.current_track: Dict = None

        # API configurations
        self.lyrics_base_url = "https://api.genius.com"
        self.lyrics_token = self.config.GENIUS_API_TOKEN

    def setup_commands(self):
        @self.bot.hybrid_command(
            name="join", with_app_command=True, description="Make me join your call"
        )
        @app_commands.describe(channel_name="Specify channel name (optional)")
        async def join(ctx, channel_name=None):
            try:
                if self.in_call(ctx):
                    self.logger.info(
                        f"{ctx.author.name} tried to make me join another channel forcefully."
                    )
                    await discord_message(
                        ctx, "Blind or what? cannot see I in another call ah?"
                    )
                    return
                await self.handle_join_command(ctx, channel_name)
            except Exception as e:
                self.logger.error(e)
                await discord_message(ctx, "I dont like you so i throw error byeee")

        @self.bot.hybrid_command(
            name="play", with_app_command=True, description="Play a song of choice"
        )
        @app_commands.describe(query="Enter song to search")
        async def play(ctx, *, query: str):
            await self.handle_play_command(ctx, query)

        @self.bot.hybrid_command(
            name="pause",
            aliases=["resume"],
            with_app_command=True,
            description="Pause or Resume song",
        )
        async def pause(ctx):
            await self.handle_pause_command(ctx)

        @self.bot.hybrid_command(
            name="skip", with_app_command=True, description="Skip next song in queue"
        )
        async def skip(ctx):
            if self.in_call(ctx) and self.queue.empty():
                await discord_message(ctx, "Queue is empty bruh... Anyhowz ah you 🎵")
            else:
                await self.handle_skip_command(ctx)

        @self.bot.hybrid_command(
            name="quit", with_app_command=True, description="Stop playing songs"
        )
        async def quit(ctx):
            await self.handle_quit_command(ctx)

        @self.bot.hybrid_command(
            name="queue",
            aliases=["q"],
            with_app_command=True,
            description="Add song to queue",
        )
        async def show_queue(ctx):
            await self.handle_queue_command(ctx)

        @self.bot.hybrid_command(
            name="clear", with_app_command=True, description="Empty song queue"
        )
        async def clear_queue(ctx):
            await self.handle_clear_command(ctx)

        @self.bot.hybrid_command(
            name="remove",
            with_app_command=True,
            description="Remove song from queue based on specified song queue position",
        )
        @app_commands.describe(position="Queue number")
        async def remove_from_queue(ctx, position: int):
            await self.handle_remove_command(ctx, position)

        @self.bot.hybrid_command(
            name="volume",
            aliases=["vol"],
            with_app_command=True,
            description="Adjust volume",
        )
        @app_commands.describe(
            volume="Volume Percentage (Range from 0 to 100. 0 = softest, 100 = loudest)"
        )
        async def set_volume(ctx, volume: int):
            await self.handle_volume_command(ctx, volume)

        @self.bot.hybrid_command(
            name="loop", with_app_command=True, description="Toggles current song loop"
        )
        async def toggle_loop(ctx):
            await self.handle_loop_command(ctx)

        @self.bot.hybrid_command(
            name="np",
            aliases=["now", "playing"],
            with_app_command=True,
            description="Returns current song",
        )
        async def now_playing(ctx):
            await self.handle_now_playing_command(ctx)

        @self.bot.hybrid_command(
            name="seek",
            with_app_command=True,
            description="Change timestamp of current track",
        )
        @app_commands.describe(timestamp="Seconds from start of track")
        async def seek(ctx, timestamp: str):
            await self.handle_seek_command(ctx, timestamp)

        @self.bot.hybrid_command(
            name="replay",
            aliases=["restart"],
            with_app_command=True,
            description="Restart queue/song????????",
        )
        async def replay(ctx):
            await self.handle_replay_command(ctx)

        @self.bot.hybrid_command(
            name="lyrics",
            aliases=["ly"],
            with_app_command=True,
            description="Display lyrics in chat",
        )
        @app_commands.describe(song_name="Enter song name to search for")
        async def lyrics(ctx, *, song_name: str = None):
            await self.handle_lyrics_command(ctx, song_name)

    # check if the url is a playlist url
    def is_playlist(self, url: str) -> bool:
        return "list=" in url and "youtube.com" in url

    async def search_music(self, query: str, url: bool = False):
        # Make this function truly asynchronous by moving the yt-dlp operation to a thread
        # Use a thread pool to handle the CPU-bound yt-dlp operation
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None, lambda: self.fetch_from_youtube(query, url)  # Use default executor
        )
        return result

    def fetch_from_youtube(self, query: str, url: bool):
        """This function runs in a separate thread"""
        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                if url:
                    info = ydl.extract_info(query, download=False)
                else:
                    info = ydl.extract_info(f"ytsearch:{query}", download=False)[
                        "entries"
                    ][0]
            return {
                "url": info["url"],
                "title": info["title"],
                "duration": info["duration"],
            }
        except Exception as e:
            self.logger.error(f"Error fetching from YouTube: {e}")
            return None

    async def search_playlist(self, url):
        """Move playlist extraction to a thread as well"""
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, lambda: self._extract_playlist(url))
        return result

    def _extract_playlist(self, url):
        """This runs in a separate thread"""
        try:
            with yt_dlp.YoutubeDL(self.playlist_opts) as ydl:
                playlist_info = ydl.extract_info(url, download=False)
                if "entries" in playlist_info:
                    return playlist_info["entries"]
                else:
                    self.logger.error("No entries found in playlist")
                    return []
        except Exception as e:
            self.logger.error(f"Error fetching playlist: {e}")
            return []

    async def process_intermediate_queue(self, ctx):
        while self.is_processing_playlist:
            track = self.pending_playlist_tracks.pop(0)
            if track.get("searched"):
                self.queue.put(track.pop("searched"))
            else:
                self.logger.info("Adding {}".format(track.get("title")))
                track_info = await self.search_music(track.get("url"), True)
                if track_info:
                    self.queue.put(track_info)
                else:
                    self.logger.error(track_info)

            if len(self.pending_playlist_tracks) == 0:
                self.is_processing_playlist = False
            asyncio.sleep(0.1)

        await discord_message(ctx, "Added the playlist to the queue... I THINK?!")

    def in_call(self, ctx) -> bool:
        """Check if bot is in a voice call."""
        return (
            ctx.guild.voice_client is not None and ctx.guild.voice_client.is_connected()
        )

    def check_valid_vc(self, ctx, channel_name) -> bool:
        """Verify if the voice channel exists."""
        channel = discord.utils.get(ctx.guild.voice_channels, name=channel_name)
        if not channel:
            asyncio.create_task(
                discord_message(
                    ctx, f"Dont even have: {channel_name}... stop trolling bruh"
                )
            )
            return False
        return True

    async def handle_join_command(self, ctx, channel_name):
        """Handle joining a voice channel."""
        if channel_name:
            channel = discord.utils.get(ctx.guild.voice_channels, name=channel_name)
        else:
            if not ctx.author.voice:
                await discord_message(
                    ctx, "You need to be in a voice channel lah retard!"
                )
                return
            channel = ctx.author.voice.channel

        if not channel:
            await discord_message(ctx, "You need to be in a voice channel lah retard!")
            return

        if ctx.guild.voice_client:
            await ctx.guild.voice_client.move_to(channel)
        else:
            await channel.connect()

        self.channel = channel
        await discord_message(
            ctx, f"I have blessed {channel.name} with my prescence! 🎵"
        )

    async def handle_play_command(self, ctx, query: str):
        """Handle playing a track."""
        await ctx.defer()
        if not self.in_call(ctx):
            await self.handle_join_command(ctx, None)

        if self.is_playlist(query):
            self.logger.info("Searching for a playlist")
            tracks = await self.search_playlist(query)
            if tracks:
                self.logger.info("Adding the songs in the playlist to the queue")
                if not self.is_processing_playlist:
                    track_info = await self.search_music(tracks.pop(0).get("url"), True)
                    self.queue.put(track_info)
                    if not ctx.guild.voice_client.is_playing():
                        await self.play_next(ctx)
                self.pending_playlist_tracks.extend(tracks)
                self.is_processing_playlist = True
                asyncio.create_task(self.process_intermediate_queue(ctx))

            else:
                self.logger.error(
                    f"There is no such playlist? i think? idk man {query}"
                )
                await discord_message(
                    ctx,
                    "Hais.. send me on wild goose chase for a playlist that dont exist? you gotta be kidding me",
                )

        else:
            track_info = await self.search_music(query)
            if not track_info:
                await discord_message(
                    ctx,
                    "Your song search as real as your gf... Search a real song leh... 😕",
                )
                return
            if self.is_processing_playlist:
                track_info["searched"] = True
                self.pending_playlist_tracks.extend(
                    [
                        track_info,
                    ]
                )
            else:
                self.queue.put(track_info)
            await discord_message(ctx, f"Added to queue: {track_info['title']} 🎵")

        if not ctx.guild.voice_client.is_playing():
            await self.play_next(ctx)

    async def play_next(self, ctx):
        """Play the next track in queue."""
        if self.loop and self.current_track:
            self.queue.put(self.current_track)

        if self.queue.empty():
            self.current_track = None
            await discord_message(
                ctx, "Queus is empty alreadyy, please add more to continues"
            )
            return

        self.current_track = self.queue.get()
        self.logger.info(f"playing {self.current_track['title']}")

        voice_client = ctx.guild.voice_client
        if not voice_client:
            return

        audio = discord.PCMVolumeTransformer(
            discord.FFmpegPCMAudio(self.current_track["url"], **self.ffmpeg_opts),
            volume=self.volume,
        )

        def after_playing(error):
            if error:
                self.logger.error(f"Error playing audio: {error}")
            asyncio.run_coroutine_threadsafe(self.play_next(ctx), self.bot.loop)

        voice_client.play(audio, after=after_playing)
        await discord_message(
            ctx, f"I shall sing: {self.current_track['title']} nowzz 🎵"
        )

    async def handle_pause_command(self, ctx):
        """Handle pausing/resuming playback."""
        if not self.in_call(ctx):
            await discord_message(
                ctx, "I am not even in a voice channel. STOP DISTURBING MY PEACE"
            )
            return

        voice_client = ctx.guild.voice_client
        if voice_client.is_playing():
            voice_client.pause()
            await discord_message(ctx, "Paused! ⏸️")
        elif voice_client.is_paused():
            voice_client.resume()
            await discord_message(ctx, "Resumed! ▶️")
        else:
            if not self.queue.empty():
                await self.play_next(ctx)

            await discord_message(
                ctx, "NOTHING IS EVEN BEING PLAYED! Are you stupid {ctx.author.id}?"
            )

    async def handle_skip_command(self, ctx):
        """Handle skipping the current track."""
        if not self.in_call(ctx):
            await discord_message(ctx, "I not even in a voice channel bruh!")
            return

        voice_client = ctx.guild.voice_client
        if voice_client.is_playing():
            voice_client.stop()
            await discord_message(ctx, "Skipped! ⏭️")
        else:
            await discord_message(ctx, "Nothing is playing!")

    async def handle_quit_command(self, ctx):
        """Handle leaving the voice channel."""
        if not self.in_call(ctx):
            await discord_message(
                ctx, "Now even in a channel to quit... You want me quit life or waht?"
            )
            return

        # Clear queue and disconnect
        while not self.queue.empty():
            self.queue.get()

        await ctx.guild.voice_client.disconnect()
        self.channel = None
        self.current_track = None
        await discord_message(
            ctx, "Bye bye! gonna go get more sleepz than all of yall 👋"
        )

    async def handle_queue_command(self, ctx):
        if self.queue.empty():
            await discord_message(ctx, "Queue is empty! Add some songs.")
            return

        queue_list = list(self.queue.queue)
        embed = discord.Embed(title="Current Queue 🎵", color=0x1DB954)

        # Add current track
        if self.current_track and isinstance(self.current_track, dict):
            try:
                embed.add_field(
                    name="Now Playing",
                    value=f"🎵 {self.current_track.get('title', 'Unknown')} [{self.current_track.get('duration', '?')}]",
                    inline=False,
                )
            except Exception as e:
                self.logger.error(f"Error displaying current track: {e}")
                embed.add_field(
                    name="Now Playing",
                    value="Error displaying current track",
                    inline=False,
                )

        # Add queue
        queue_text = ""
        for i, track in enumerate(queue_list, 1):
            try:
                if isinstance(track, dict) and "title" in track and "duration" in track:
                    queue_text += f"{i}. {track['title']} [{track['duration']}]\n"
                else:
                    queue_text += f"{i}. [Invalid track format]\n"
                    self.logger.error(
                        f"Invalid track format in queue position {i}: {type(track)}"
                    )
            except Exception as e:
                queue_text += f"{i}. [Error displaying track]\n"
                self.logger.error(f"Error displaying track at position {i}: {e}")

            if i >= 10:  # Show only first 10 items
                remaining = self.queue.qsize() - 10
                if remaining > 0:
                    queue_text += f"\n*...and {remaining} more tracks*"
                break

        if queue_text:
            embed.add_field(name="Up Next", value=queue_text, inline=False)

        await discord_embed(ctx, embed)

    async def handle_clear_command(self, ctx):
        """Clear the queue."""
        while not self.queue.empty():
            self.queue.get()
        await discord_message(ctx, "Queue cleared! 🧹")

    async def handle_remove_command(self, ctx, position: int):
        """Remove a track from the queue."""
        if position < 1 or position > self.queue.qsize():
            await discord_message(
                ctx,
                "You dont even have that many songs queued bruhhhh! Please check the queue first.",
            )
            return

        queue_list = list(self.queue.queue)
        removed_track = queue_list.pop(position - 1)

        self.queue = queue.Queue()
        for track in queue_list:
            self.queue.put(track)

        await discord_message(
            ctx, f"Removed '{removed_track['title']}' from the queue! ❌"
        )

    async def handle_volume_command(self, ctx, volume: int):
        """Set the volume."""
        if not 0 <= volume <= 100:
            await discord_message(ctx, "Volume must be between 0 and 100!")
            return

        if not ctx.guild.voice_client:
            await discord_message(
                ctx,
                "I NOT EVEN IN CALL WITH YOU!!! gonna make me dunb like you if i am in the call frfr",
            )
            return

        self.volume = volume / 100
        if ctx.guild.voice_client.source:
            ctx.guild.voice_client.source.volume = self.volume

        await discord_message(ctx, f"Volume set to {volume}% 🔊")

    async def handle_loop_command(self, ctx):
        """Toggle loop mode."""
        self.loop = not self.loop
        status = "enabled" if self.loop else "disabled"
        await discord_message(ctx, f"Loop mode {status} 🔁")

    async def handle_now_playing_command(self, ctx):
        """Show the currently playing track."""
        if not self.current_track:
            await discord_message(ctx, "Nothing is playing right now!")
            return

        embed = discord.Embed(
            title="Now Playing 🎵",
            description=f"**{self.current_track['title']}**",
            color=0x1DB954,
        )
        embed.add_field(name="Duration", value=self.current_track["duration"])

        await discord_message(ctx, embed=embed)

    async def handle_seek_command(self, ctx, timestamp: str):
        """Seek to a position in the track."""
        if not ctx.guild.voice_client or not ctx.guild.voice_client.is_playing():
            await discord_message(
                ctx,
                "YOU DEAF OR WHAT... NOTHING EVEN BEING PLAYE I SEEK YOUR MUM OUT LAH!",
            )
            return

        try:
            parts = timestamp.split(":")
            if len(parts) == 2:
                minutes, seconds = map(int, parts)
                seek_position = minutes * 60 + seconds
            else:
                seek_position = int(timestamp)

            await discord_message(ctx, f"Seeking to {timestamp}... ⏩")

        except ValueError:
            await discord_message(
                ctx, "Invalid timestamp format! Use MM:SS or seconds."
            )

    async def handle_replay_command(self, ctx):
        """Replay the current track."""
        if not self.current_track:
            await discord_message(
                ctx, "NOTHING IS EVEN BEING PLAYED! Are you DEAF {ctx.author.id}?"
            )
            return

        voice_client = ctx.guild.voice_client
        if not voice_client:
            await discord_message(
                ctx,
                "I NOT EVEN IN CALL WITH YOU!!! gonna make me dunb like you if i am in the call frfr",
            )
            return

        voice_client.stop()
        audio = discord.PCMVolumeTransformer(
            discord.FFmpegPCMAudio(self.current_track["url"], **self.ffmpeg_opts),
            volume=self.volume,
        )

        def after_playing(error):
            if error:
                self.logger.error(f"Error playing audio: {error}")
            asyncio.run_coroutine_threadsafe(self.play_next(ctx), self.bot.loop)

        voice_client.play(audio, after=after_playing)
        await discord_message(ctx, f"🔄 Replaying: {self.current_track['title']}")

    async def handle_lyrics_command(self, ctx, song_name: str = None):
        """Fetch and display lyrics."""
        await ctx.defer()
        if not song_name and not self.current_track:
            await discord_message(ctx, "Either specify a song or play something first!")
            return

        search_query = song_name if song_name else self.current_track["title"]
        search_query = re.sub(
            r"\(feat\..*?\)|\(ft\..*?\)|\(with.*?\)|\[.*?\]|\(.*?remix.*?\)",
            "",
            search_query,
            flags=re.IGNORECASE,
        )
        search_query = search_query.strip()

        try:
            searching_msg = await discord_message(
                ctx, f"🔎 Searching for lyrics of: {search_query}"
            )
            lyrics = await self.fetch_lyrics(search_query)

            if not lyrics:
                await searching_msg.edit(
                    content="❌ Couldn't find lyrics for this song!"
                )
                return

            chunks = self.split_lyrics(lyrics)
            await searching_msg.delete()

            for i, chunk in enumerate(chunks):
                embed = discord.Embed(
                    title=(
                        f"Lyrics for: {search_query}"
                        if i == 0
                        else f"Lyrics (continued {i+1}/{len(chunks)})"
                    ),
                    description=chunk,
                    color=0x1DB954,
                )
                if i == 0:
                    embed.set_footer(text="Lyrics powered by Genius")
                await discord_message(ctx, embed=embed)

        except Exception as e:
            self.logger.error(f"Error fetching lyrics: {e}")
            await discord_message(ctx, "❌ An error occurred while fetching lyrics!")

    async def fetch_lyrics(self, song_name: str) -> str:
        """Fetch lyrics from Genius API."""
        if not self.lyrics_token:
            self.logger.error("No Genius API token configured!")
            return None

        headers = {"Authorization": f"Bearer {self.lyrics_token}"}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.lyrics_base_url}/search",
                    headers=headers,
                    params={"q": song_name},
                ) as resp:
                    if resp.status != 200:
                        return None

                    data = await resp.json()
                    if not data["response"]["hits"]:
                        return None

                    song_url = data["response"]["hits"][0]["result"]["url"]

                    async with session.get(song_url) as lyrics_resp:
                        if lyrics_resp.status != 200:
                            return None

                        html = await lyrics_resp.text()

                        lyrics_div = re.search(
                            r'<div class="lyrics">(.*?)</div>', html, re.DOTALL
                        )
                        if lyrics_div:
                            lyrics = lyrics_div.group(1)
                            lyrics = re.sub(r"<[^>]+>", "", lyrics)
                            lyrics = re.sub(r"&#x27;", "'", lyrics)
                            lyrics = re.sub(r"&quot;", '"', lyrics)
                            return lyrics.strip()

                        return None

        except Exception as e:
            self.logger.error(f"Error in fetch_lyrics: {e}")
            return None

    def split_lyrics(self, lyrics: str, max_length: int = 1000) -> List[str]:
        """Split lyrics into chunks that fit in Discord embeds."""
        chunks = []
        current_chunk = ""

        for line in lyrics.split("\n"):
            if len(current_chunk) + len(line) + 1 > max_length:
                chunks.append(current_chunk.strip())
                current_chunk = line
            else:
                current_chunk += f"\n{line}" if current_chunk else line

        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks
