import discord
import os
import logging
import httpx

from discord.ext import commands
from dotenv import load_dotenv
from datetime import datetime, timedelta
from helper import *


load_dotenv()

logger = logging.getLogger(__name__)
logging.basicConfig(filename="MCM.log", level=logging.INFO)

intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(intents=intents, command_prefix="%")

last_stop = datetime.now() - timedelta(hours=1)
last_start = datetime.now() - timedelta(hours=1)

allowed_users = (304976615723499533, 476162085827379231)
allowed_channels = {"minecraft": "Vanilla", "atm9": "ATM9"}


url = "https://admin.tntcraft.xyz/api"


def format_timedelta(delta):
    total_seconds = int(delta.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours}h {minutes}m {seconds}s"


def get_now() -> str:
    return datetime.now().time().strftime("%H:%M")


@client.event
async def on_ready() -> None:
    logger.info("Bot is Online and Ready!")


@client.command(name="test")
async def test(ctx) -> None:
    logging.info(ctx)
    logging.info(ctx.author.id)


@client.command(name="start")
async def start(ctx) -> None:
    global last_start
    global allowed_users
    global url
    global allowed_channels

    logging.info(
        f"{ctx.author} has used to start command at {get_now()} for {allowed_channels[ctx.channel.name]}"
    )

    if ctx.channel.name not in allowed_channels:
        logging.error(f"Wrong Channel. {ctx.channel.name} was used instead.")
        await ctx.send(f"Please use the correct channel: {allowed_channels}")
        raise Exception("Incorrect Channel")

    if ctx.author.id not in allowed_users:
        if (datetime.now() - last_start) <= timedelta(minutes=59):
            error_message = f"It has only been {format_timedelta(datetime.now() - last_start)} since the server was last started by as user please try again at {(last_start + timedelta(hours=1)).strftime('%Y-%m-%d %H:%M')}"
            logging.error(error_message)
            await ctx.send(error_message)
            raise Exception("Spamming Start!")

    logging.info("starting server " + allowed_channels[ctx.channel.name])

    try:
        params = {
            "apikey": os.getenv("api_key"),
            "uuid": os.getenv(f"instance_id_{ctx.channel.name}"),
            "daemonId": os.getenv(f"daemon_id_{ctx.channel.name}"),
        }
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url=url + "/protected_instance/open", params=params
            )
        if response.status_code == 500:
            if (
                response.json()["data"]
                == "The instance is running and cannot be started again"
            ):
                await ctx.send(
                    "you idot, the serer is alreadu on. stop spamning or i come to ur house and slap u"
                )
                raise Exception("idot turning on server thats alr on")
            else:
                await ctx.send(
                    "Contact <@304976615723499533> or <@476162085827379231> to turn on machine then try again."
                )
                raise Exception("Machine is turned off")
        elif response.status_code != 200:
            raise Exception("Machine is turned off")

        message = (
            allowed_channels[ctx.channel.name] + f" has been started at {get_now()}"
        )
        logging.info(message)
        await ctx.send(message)
        if ctx.author.id not in allowed_users:
            last_start = datetime.now()

    except Exception as e:
        logging.error(e)
        await ctx.send(f"Start process has failed.")


@client.command(name="stop")
async def stop(ctx):
    global allowed_users
    global allowed_channels

    if ctx.channel.name not in allowed_channels:
        logging.error(f"Wrong Channel. {ctx.channel.name} was used instead.")
        await ctx.send(f"Please use the correct channel " + str(allowed_channels))
        raise Exception("Incorrect Channel")

    if ctx.channel.name == "minecraft" and ctx.author.id not in allowed_users:
        error_message = f"You are not authorised to use this command."
        await ctx.send(error_message)
        logging.error(f"Unathorised use of stop command!: {ctx.author}")
        raise Exception("Unauthorised Stop!")

    logging.info("stopping " + allowed_channels[ctx.channel.name])

    try:
        params = {
            "apikey": os.getenv("api_key"),
            "uuid": os.getenv(f"instance_id_{ctx.channel.name}"),
            "daemonId": os.getenv(f"daemon_id_{ctx.channel.name}"),
        }
        if not players_online(allowed_channels[ctx.channel.name]):
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url=url + "/protected_instance/stop", params=params
                )
        else:
            message = "Unable to stop. There are players online."
            await ctx.send(message)
            raise Exception(message)

        if response.status_code != 200:
            if "The remote node is unavailable!" in response.json()["data"]:
                await ctx.send(
                    "the machine is of idiot, can u not spam or misuse the command pls."
                )
                raise Exception("machine off")
            elif (
                response.json()["data"]
                == "The instance is not running and cannot be stopped."
            ):
                await ctx.send(
                    "Verily, thou dolt, the server hath long since been extinguished!"
                )
                raise Exception("stupid")
            else:
                await ctx.send(
                    "I also dk why it never work... never bothered testing :)"
                )
                raise Exception("IDK WHATS WRONG ALSO!!!")

        message = (
            allowed_channels[ctx.channel.name] + f" has been stopped at {get_now()}"
        )
        logging.info(message)
        await ctx.send(message)

    except Exception as e:
        logging.error(e)
        await ctx.send(f"Stop process has failed.")


logging.info(f"{get_now}  Starting Bot...")
client.run(os.getenv("discord_token"))
