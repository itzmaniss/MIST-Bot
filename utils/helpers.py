from datetime import datetime
from typing import Union
from mcstatus import JavaServer
from utils.logger import Logger
from config.config import Config
import discord


def get_timestamp() -> str:
    """Get current timestamp in consistent format."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def format_duration(seconds: int) -> str:
    """Format seconds into human-readable duration."""
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)

    if hours > 0:
        return f"{hours}:{minutes:02d}:{seconds:02d}"
    return f"{minutes}:{seconds:02d}"


def is_url(text: str) -> bool:
    """Check if text is a URL."""
    return text.startswith(("http://", "https://"))


def players_online(server_name: str) -> bool:
    server_ip = Config.SERVER_IP
    if len(server_ip) == 0:
        return False

    server = JavaServer.lookup(server_ip[server_name])
    status = server.status()

    if status:
        Logger.error(f"There are still {status.players.online} players online.")
        return status.players.online > 0

    return False


def format_timedelta(delta):
    total_seconds = int(delta.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours}h {minutes}m {seconds}s"

async def discord_message(ctx, msg) -> None:
    print(ctx.message)
    try:
        await ctx.send(msg)
    except Exception as e:
        # If the interaction is no longer valid, try sending a regular message
        await ctx.channel.send(msg)
        print(e.args[0])
