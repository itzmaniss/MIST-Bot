from features.base import BotFeature
from config.config import Config
from utils.logger import Logger


class HelpFeature(BotFeature):
    def __init__(self, bot):
        BotFeature.__init__(self, bot)
        self.ongoing_pings = {}
        self.logger = Logger("Smokers Bot")
        self.config = Config

    def setup_commands(self):
        @self.bot.hybrid_command(name="help", with_app_command=True, description="Shows all commands")
        async def help(ctx):
            await ctx.send("""```
Minecraft Server:
start <server>
stop <server>

Music:
ask manis fill this himself ples
                           ```""")