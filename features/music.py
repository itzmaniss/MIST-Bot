from features.base import BotFeature
from utils.logger import Logger
from config.config import Config
import yt_dlp
import discord

class MusicFeature(BotFeature):
    def __init__(self, bot):
        super().__init__(bot)
        self.ydl_opts = {
            'format': 'bestaudio/best',
            'noplaylist': True,
            'quiet': True
        }
        self.logger = Logger("Music Bot")
    
    def setup_commands(self):
        @self.bot.command(name="join")
        async def join(ctx, channel_name=None):
            if channel_name == None:
                
                await self.handle_join(ctx)


        @self.bot.command(name="play")
        async def play(ctx, *, query: str):
            await self.handle_play_command(ctx, query)
    
    async def handle_play_command(self, ctx, query: str):
        # Your implementation here
        pass
