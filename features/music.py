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
        self.config = Config()
        self.logger = Logger("Music Bot")
        self.queue = []
        self.channel = 0
    
    def setup_commands(self):
        @self.bot.command(name="join")
        async def join(ctx, channel_name=None):
            try:
                if self.in_call():
                    self.logger.info(f"{ctx.author.name} tried to make me join another forcefully . Help me ples.")
                    await ctx.send("Cannot see I in another call ah?")
                if channel_name != None:
                    if not self.check_valid_vc(ctx, channel_name):
                        return
                await self.handle_join_command(ctx, channel_name)
                    
                    
            
            except Exception as e:
                self.logging.error(e)
                await ctx.send("Sorry there was an error joining the call")


        @self.bot.command(name="play")
        async def play(ctx, *, query: str):
            await self.handle_play_command(ctx, query)
        
    def search_music(query) -> str:
        pass

    def in_call(self, ctx) -> bool:
        pass
    
    def check_valid_vc(self, ctx, channel_name) -> bool:
        pass

    async def handle_join_command(self, ctx, channel_name):
        self.channel = ctx.message.author.voice.voice_channel

        pass

    async def handle_play_command(self, ctx, query: str):
        pass

    async def handle_pause_command(self, ctx):
        pass

    async def handle_skip_command(self, ctx):
        pass

    async def handle_quit_command(self, ctx):
        self.channel = 0
        pass
