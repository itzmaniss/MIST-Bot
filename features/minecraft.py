from features.base import BotFeature
from config.config import Config
from utils.helpers import get_timestamp, players_online, format_timedelta
from utils.logger import Logger
from core.server_manager import ServerManager
from datetime import timedelta, datetime
from discord import app_commands

logger = Logger("minecraft_bot")


class MinecraftFeature(BotFeature):
    def __init__(self, bot):
        BotFeature.__init__(self, bot)
        self.last_stop = datetime.now() - timedelta(hours=1)
        self.last_start = datetime.now() - timedelta(hours=1)
        self.server = ServerManager(Config.API_URL, Config.API_KEY)

    def setup_commands(self):
        @self.bot.hybrid_command(name="start", with_app_command=True, description="Start specified server")
        @app_commands.describe(server="Server name")
        @app_commands.choices(server=[ # Find out how to un-hardcode this
            app_commands.Choice(name='Vanilla', value='vanilla'),
            app_commands.Choice(name='ATM9', value='atm9')
        ])
        async def start(ctx, server):
            server = server.lower()
            await self.handle_start_command(ctx, server)

        @self.bot.hybrid_command(name="stop", with_app_command=True, description="Stop specified server")
        @app_commands.describe(server="Server name")
        @app_commands.choices(server=[ # Find out how to un-hardcode this
            app_commands.Choice(name='Vanilla', value='vanilla'),
            app_commands.Choice(name='ATM9', value='atm9')
        ])
        async def stop(ctx, server) -> None:
            server = server.lower()
            await self.handle_stop_command(ctx, server)

    async def handle_start_command(self, ctx, arg):

        logger.info(
            f"{ctx.author} has used to start command at {get_timestamp()} for {arg}"
        )

        if ctx.channel.name not in Config.ALLOWED_CHANNELS:
            logger.error(f"Wrong Channel. {ctx.channel.name} was used instead.")
            await ctx.send(f"Please use the correct channel: {Config.ALLOWED_CHANNELS}")
            raise Exception("Incorrect Channel")

        if ctx.author.id not in Config.ALLOWED_USERS:
            if (get_timestamp() - self.last_start) <= timedelta(minutes=59):
                error_message = f"It has only been {format_timedelta(get_timestamp() - self.last_start)} since the server was last started by as user please try again at {(self.last_start + timedelta(hours=1)).strftime('%Y-%m-%d %H:%M')}"
                logger.error(error_message)
                await ctx.send(error_message)
                raise Exception("Spamming Start!")

        logger.info("starting server " + arg)

        try:

            response = await self.server.start_server(
                Config.UUID[arg], Config.DAEMON_ID[arg]
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

            message = arg + f" has been started at {get_timestamp()}"
            logger.info(message)
            await ctx.send(message)
            if ctx.author.id not in Config.ALLOWED_USERS:
                self.last_start = get_timestamp()

        except Exception as e:
            logger.error(e)
            await ctx.send(f"Start process has failed.")

    async def handle_stop_command(self, ctx, arg) -> None:

        if ctx.channel.name not in Config.ALLOWED_CHANNELS:
            logger.error(f"Wrong Channel. {ctx.channel.name} was used instead.")
            await ctx.send(
                f"Please use the correct channel " + str(Config.ALLOWED_CHANNELS)
            )
            raise Exception("Incorrect Channel")

        if (
            ctx.channel.name == "minecraft"
            and ctx.author.id not in Config.ALLOWED_USERS
        ):
            error_message = f"You are not authorised to use this command."
            await ctx.send(error_message)
            logger.error(f"Unathorised use of stop command!: {ctx.author}")
            raise Exception("Unauthorised Stop!")

        logger.info("stopping " + arg)

        try:
            if not players_online(arg):
                response = await self.server.stop_server(
                    Config.UUID[arg], Config.DAEMON_ID[arg]
                )

            else:
                message = "Unable to stop. There are players online."
                await ctx.send(message)
                raise Exception(message)

        except Exception as e:
            logger.error(e)
            await ctx.send(
                "the serevr is alreigty down you iiot. shoo. turn around 180 degrees, and walk straight for me pls tq :3"
            )
            raise Exception("server down")

        logger.info(response)
        if response.status_code != 200:
            data = response.json()["data"]
            logger.error(f"code {response.status_code}, data: {data}")
            if (
                "The remote node is unavailable!" in response.json()["data"]
            ):  # should not happen
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

        message = arg + f" has been stopped at {get_timestamp()}"
        logger.info(message)
        await ctx.send(message)
