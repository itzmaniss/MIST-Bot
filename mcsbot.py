import discord
import os
import logging
import mcsmanager as mcs

from discord.ext import commands
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

logger = logging.getLogger(__name__)
logging.basicConfig(filename="MCM.log", level=logging.INFO)

intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(intents=intents, command_prefix = "%")

last_stop = datetime.now() - timedelta(hours = 1)
last_start = datetime.now() - timedelta(hours = 1)
allowed_users = (304976615723499533, 476162085827379231)

def format_timedelta(delta):
    total_seconds = int(delta.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours}h {minutes}m {seconds}s"


@client.event
async def on_ready():  
    logger.info("Bot is Online and Ready!")

@client.command( name = "test")
async def test(ctx):
    logging.info(ctx)
    logging.info(ctx.author.id)

@client.command(name = "start")
async def start(ctx):
    global last_start
    global allowed_users

    if not ctx.channel.name == "minecraft": 
        logging.error(f"Wrong Channel. {ctx.channel.name} was used instead.")
        await ctx.send(f"Please use the correct channel: minecraft")
        raise Exception("Incorrect Channel")

    if ctx.author.id not in allowed_users:
        if (datetime.now() - last_start) <= timedelta(minutes=59):
            error_message = f"It has only been {format_timedelta(datetime.now() - last_start)} since the server was last started by as user please try again at {(last_start + timedelta(hours=1)).strftime('%Y-%m-%d %H:%M')}"
            logging.error(error_message)
            await ctx.send(error_message)
            raise Exception("Spamming Start!")

    logging.info("starting vanilla")

    try:
        await mcs.start()

        message = f"Vanilla has been started at {datetime.now().time().strftime('%H:%M')}"
        logging.info(message)
        await ctx.send(message)
        if ctx.author.id not in allowed_users:
            last_start = datetime.now()

    except Exception as e:
        logging.error(e)
        await ctx.send(f"Start process has failed.")

@client.command(name = "stop")
async def stop(ctx):
    global last_stop
    global allowed_users

    if not ctx.channel.name == "minecraft": 
        logging.error(f"Wrong Channel. {ctx.channel.name} was used instead.")
        await ctx.send(f"Please use the correct channel: minecraft")
        raise Exception("Incorrect Channel")

    if ctx.author.id not in allowed_users:
        if (datetime.now() - last_stop) <= timedelta(minutes=2):
            error_message = f"It has only been {format_timedelta(datetime.now() - last_start)} since the server was last started by as user please try again at {(last_start + timedelta(hours=1)).strftime('%Y-%m-%d %H:%M')}"
            logging.error(error_message)
            await ctx.send(error_message)
            raise Exception("Spamming Stop!")

    logging.info("stopping vanilla")

    try:
        await mcs.stop()

        message = f"Vanilla has been stopped at {datetime.now().time().strftime('%H:%M')}"
        logging.info(message)
        await ctx.send(message)
        if ctx.author.id not in allowed_users:
            last_start = datetime.now()

    except Exception as e:
        logging.error(e)
        await ctx.send(f"Stop process has failed.")

logging.info(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  Starting Bot...")
client.run(os.getenv("discord_token"))