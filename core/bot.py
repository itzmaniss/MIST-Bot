import discord
from discord.ext import commands
from datetime import datetime
from config.config import Config
import logging


class DiscordBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True

        super().__init__(command_prefix=Config.COMMAND_PREFIX, intents=intents, help_command=None)

        self.logger = logging.getLogger("DiscordBot")
        self.startup_time = datetime.now()

    async def setup_hook(self):
        await self.tree.sync()
        self.logger.info("Synced command tree.")

    async def on_ready(self):
        self.logger.info(f"Logged in as {self.user.name} (ID: {self.user.id})")
        await self.change_presence(
            activity=discord.Game(name=f"{Config.COMMAND_PREFIX}help for commands"),
            status=discord.Status.dnd
        )

    def run_bot(self):
        self.logger.info("Starting bot...")
        self.run(Config.DISCORD_TOKEN)
