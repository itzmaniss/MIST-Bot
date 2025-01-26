from features.base import BotFeature
from config.config import Config
from utils.logger import Logger
import asyncio
import discord

class SmokingFeature(BotFeature):
    def __init__(self, bot):
        BotFeature.__init__(self, bot)
        self.ongoing_pings = {}
        self.logger = Logger("Smokers Bot")
        self.config = Config

    def setup_commands(self):
        @self.bot.command(name="wakey")
        async def wakey(ctx, user):
            if self.valid_smoker(ctx):
                try:
                    self.logger.info(f"{ctx.author.name} is waking up {await self.name(ctx, user)}")
                    await self.handle_wakey(ctx, user)
                except Exception as e:
                    self.logger.error(f"Error in wakey command: {e}")
                    await ctx.send("An error occurred while processing the command.")
            else:
                self.logger.info(f"a non-smoker {await self.name(ctx)} tried to abuse this command frfr")
        
        @self.bot.command(name="woken")
        async def woken(ctx, user=None):
            if not self.valid_smoker(ctx):
                await ctx.send("You are not authorized to use this command.")
                return
            else:
                try:
                    await self.handle_woken(ctx, user) 
                except Exception as e:
                    self.logger.error(f"Error in wakey command: {e}")
                    await ctx.send("An error occurred while processing the command.")

        @self.bot.command(name = "test")
        async def test(ctx):
            if self.valid_smoker(ctx):
                self.logger.info(f"{ctx.author.name} is a smoker")


    def valid_smoker(self, ctx) -> bool:
        roles = ctx.author.roles
        return discord.utils.get(roles, id=self.config.SMOKER_ID)
    
    
    async def name(self, ctx, user_id) -> str:
        if user_id is None:
            return ctx.author.name
        
        try:
            # Handle mention
            if isinstance(user_id, str) and user_id.startswith('<@') and user_id.endswith('>'):
                user_id = int(user_id.strip('<@!>'))
            
            member = await ctx.guild.fetch_member(user_id)
            return member.name
        except (discord.NotFound, ValueError):
            return str(user_id)

    async def handle_wakey(self, ctx, user):
        self.ongoing_pings[user] = True
        try:
            for _ in range(20):
                if not self.ongoing_pings.get(user, False):
                    break
                await ctx.send(f"wake up {user}.Time to smoke you {self.config.WORD_1}")
                await asyncio.sleep(1)
        except Exception as e:
            self.logger.error(f"Error in handle_wakey: {e}")
        finally:
            self.ongoing_pings.pop(user, None)
        

    async def handle_woken(self, ctx, user):
        if user == None:
            user = f"<@{ctx.author.id}>"
        if user in self.ongoing_pings:
            self.ongoing_pings[user] = False
        self.logger.info(f"{await self.name(ctx, user)} has awoken")
        await ctx.send(f"Thanks for waking up{user}")
