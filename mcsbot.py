import discord
import os
import logging
import httpx

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

url = "https://admin.tntcraft.xyz/api"

def format_timedelta(delta):
    total_seconds = int(delta.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours}h {minutes}m {seconds}s"

def get_now() -> str:
    return datetime.now().time().strftime('%H:%M')


@client.event
async def on_ready() -> None:  
    logger.info("Bot is Online and Ready!")

@client.command( name = "test")
async def test(ctx) -> None:
    logging.info(ctx)
    logging.info(ctx.author.id)

@client.command(name = "start")
async def start(ctx) -> None:
    global last_start
    global allowed_users
    global url

    logging.info(f"{ctx.author} has used to start command at {get_now()}")

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
        params = {
            "apikey": os.getenv("api_key"),
            "uuid": os.getenv("instance_id"),
            "daemonId": os.getenv("daemon_id")
        }
        async with httpx.AsyncClient() as client:
            response = await client.get(url=url+"/protected_instance/open", params=params)
        if response.status_code == 500:
            await ctx.send("Contact KKYH to turn on machine then try again.")
            raise Exception("Machine is turned off")
        elif response.status_code != 200:
            raise Exception("Machine is turned off")

        message = f"Vanilla has been started at {get_now()}"
        logging.info(message)
        await ctx.send(message)
        if ctx.author.id not in allowed_users:
            last_start = datetime.now()

    except Exception as e:
        logging.error(e)
        await ctx.send(f"Start process has failed.")

@client.command(name = "stop")
async def stop(ctx):
    global allowed_users

    if not ctx.channel.name == "minecraft": 
        logging.error(f"Wrong Channel. {ctx.channel.name} was used instead.")
        await ctx.send(f"Please use the correct channel: minecraft")
        raise Exception("Incorrect Channel")

    if ctx.author.id not in allowed_users:
        error_message = f"You are not authorised to use this command."
        await ctx.send(error_message)
        logging.error(f"Unathorised use of stop command!: {ctx.author}")
        raise Exception("Unauthorised Stop!")

    logging.info("stopping vanilla")

    try:
        params = {
            "apikey": os.getenv("api_key"),
            "uuid": os.getenv("instance_id"),
            "daemonId": os.getenv("daemon_id")
        }
        async with httpx.AsyncClient() as client:
            response = await client.get(url=url+"/protected_instance/stop", params=params)

        if response.status_code != 200:
            await ctx.send("I also dk why it never work... never bothered testing :)")
            raise Exception("IDK WHATS WRONG ALSO!!!")

        message = f"Vanilla has been stopped at {get_now()}"
        logging.info(message)
        await ctx.send(message)

    except Exception as e:
        logging.error(e)
        await ctx.send(f"Stop process has failed.")

logging.info(f"{get_now}  Starting Bot...")
client.run(os.getenv("discord_token"))