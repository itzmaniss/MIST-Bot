from features.base import BotFeature
from utils.logger import Logger
from utils.counter import CounterUtils
from config.config import Config
import discord
from discord.ext import commands
from typing import Optional
from datetime import datetime


class CountingFeature(BotFeature):
    def __init__(self, bot):
        super().__init__(bot)
        self.logger = Logger("Counting Bot")
        self.counter = CounterUtils()
        self.config = Config

    def setup_commands(self):
        @self.bot.command(name="count_help")
        async def help(ctx):
            """Show help information for counting commands."""
            self.logger.info(f"User {ctx.author.name} requested count help")
            await self.handle_help_command(ctx)

        @self.bot.command(name="count_stats")
        async def stats(ctx, user: discord.Member = None):
            """Show counting statistics for a user."""
            target_user = user or ctx.author
            self.logger.info(
                f"Stats requested by {ctx.author.name} for user {target_user.name}"
            )
            await self.handle_stats_command(ctx, target_user)

        @self.bot.command(name="count_top")
        async def top(ctx):
            """Show top counters leaderboard."""
            self.logger.info(f"Top counters requested by {ctx.author.name}")
            await self.handle_top_command(ctx)

        @self.bot.command(name="prime_top")
        async def prime_top(ctx):
            """Show top prime number counters leaderboard."""
            self.logger.info(f"Prime leaderboard requested by {ctx.author.name}")
            await self.handle_prime_top_command(ctx)

        @self.bot.command(name="fail_top")
        async def fail_top(ctx):
            """Show top failure leaderboard."""
            self.logger.info(f"Fail leaderboard requested by {ctx.author.name}")
            await self.handle_fail_top_command(ctx)

        @self.bot.command(name="next_prime")
        async def next_prime(ctx):
            """Show the next prime number in the sequence."""
            self.logger.info(f"Next prime requested by {ctx.author.name}")
            await self.handle_next_prime_command(ctx)

        @self.bot.event
        async def on_message(message):
            if message.author.bot:
                return

            # Process commands first
            if message.content.startswith(self.bot.command_prefix):
                await self.bot.process_commands(message)
                return

            # Check if this is a counting channel
            if message.channel.name not in self.config.COUNTING_CHANNELS:
                return

            # Process the count
            try:
                await self.process_count(message)
            except Exception as e:
                self.logger.error(f"Error processing count: {e}")

    async def process_count(self, message):
        """Process a counting message."""
        self.logger.info(f"Message received from {message.author.name}: {message.content}")
        
        # First check if this looks like a counting attempt
        # Try to evaluate the expression first
        evaluated_value = self.counter._evaluate_expression(message.content)
        
        # If we couldn't evaluate it as a number, treat it as regular chat
        if evaluated_value is None:
            # Allow regular chat messages to pass through without any reaction
            return
                
        # At this point, we know it's a counting attempt
        self.logger.info(f"Count attempt from {message.author.name}: {message.content} (evaluated to: {evaluated_value})")
        
        # Validate the count
        result = self.counter.validate_count(
            str(evaluated_value),
            str(message.guild.id),
            str(message.author.id)
        )

        if not result:
            self.logger.error(f"Invalid count from {message.author.name}: {message.content} (evaluated to: {evaluated_value})")
            await message.add_reaction("❌")
            await message.channel.send(
                f"{message.author.mention} ruined the count! Starting over from 1.\n"
                f"Debug info - Your input '{message.content}' evaluated to: {evaluated_value}"
            )
            return

        is_valid, is_prime, _ = result

        if is_valid:
            count_value = evaluated_value
            self.logger.info(f"Valid count from {message.author.name}: {count_value}" + (" (PRIME)" if is_prime else ""))
            
            # Log milestones
            if count_value % 100 == 0:
                self.logger.info(f"Century milestone reached: {count_value}")
            if count_value % 1000 == 0:
                self.logger.info(f"Millennium milestone reached: {count_value}")
                
            if is_prime:
                await message.add_reaction("🔢")
            else:
                await message.add_reaction("✅")
        else:
            self.logger.error(f"Invalid sequence from {message.author.name}: expected next number")
            await message.add_reaction("❌")
            await message.channel.send(
                f"{message.author.mention} ruined the count! Starting over from 1."
            )

    async def handle_help_command(self, ctx):
        """Handle the count_help command."""
        embed = discord.Embed(
            title="Counting Bot Help",
            description="Count numbers sequentially with support for math expressions!",
            color=0x3498DB,
        )

        embed.add_field(
            name="Commands",
            value="""
                `/count_help` - Show this help message
                `/count_stats [@user]` - Show user statistics
                `/count_top` - Show top counters
                `/prime_top` - Show top prime counters
                `/fail_top` - Show top failures
                `/next_prime` - Show next prime number
            """,
            inline=False,
        )

        embed.add_field(
            name="Counting Rules",
            value="""
                • Type the next number in sequence
                • No counting twice in a row
                • Supports math expressions (e.g., `2+2`, `sqrt(16)`)
                • Supports number words (e.g., 'four', 'twenty')
                • ✅ - Correct number
                • 🔢 - Prime number
                • ❌ - Wrong number
            """,
            inline=False,
        )

        await ctx.send(embed=embed)

    async def handle_stats_command(self, ctx, user: discord.Member):
        """Handle the count_stats command."""
        stats = self.counter.get_user_stats(str(ctx.guild.id), str(user.id))
        if not stats:
            await ctx.send(f"{user.mention} hasn't counted anything yet!")
            return

        embed = discord.Embed(
            title=f"Counting Stats for {user.display_name}", color=0x3498DB
        )

        embed.add_field(
            name="Total Counts", value=str(stats["total_counts"]), inline=True
        )
        embed.add_field(
            name="Prime Numbers", value=str(stats["prime_counts"]), inline=True
        )
        embed.add_field(
            name="Failed Counts", value=str(stats["total_fails"]), inline=True
        )
        embed.add_field(
            name="Highest Count", value=str(stats["highest_count"]), inline=True
        )

        if stats["last_fail_date"]:
            fail_date = datetime.fromtimestamp(float(stats["last_fail_date"]))
            embed.add_field(
                name="Last Fail",
                value=fail_date.strftime("%Y-%m-%d %H:%M"),
                inline=True,
            )

        await ctx.send(embed=embed)

    async def handle_top_command(self, ctx):
        """Handle the count_top command."""
        leaders = self.counter.get_leaderboard(str(ctx.guild.id), "counts")
        await self.send_leaderboard(ctx, "Top Counters", leaders)

    async def handle_prime_top_command(self, ctx):
        """Handle the prime_top command."""
        leaders = self.counter.get_leaderboard(str(ctx.guild.id), "primes")
        await self.send_leaderboard(ctx, "Top Prime Counters", leaders)

    async def handle_fail_top_command(self, ctx):
        """Handle the fail_top command."""
        leaders = self.counter.get_leaderboard(str(ctx.guild.id), "fails")
        await self.send_leaderboard(ctx, "Top Failures", leaders)

    async def send_leaderboard(self, ctx, title: str, leaders):
        """Helper function to send a leaderboard embed."""
        if not leaders:
            await ctx.send("No data available for the leaderboard!")
            return

        embed = discord.Embed(title=title, color=0x3498DB)
        for i, (score, user_id) in enumerate(leaders, 1):
            try:
                user = await self.bot.fetch_user(int(user_id))
                embed.add_field(
                    name=f"#{i} {user.display_name}", value=str(score), inline=False
                )
            except discord.NotFound:
                embed.add_field(
                    name=f"#{i} Unknown User", value=str(score), inline=False
                )

        await ctx.send(embed=embed)

    async def handle_next_prime_command(self, ctx):
        """Handle the next_prime command."""
        next_prime = self.counter.get_next_prime(str(ctx.guild.id))
        await ctx.send(f"The next prime number is {next_prime}")
