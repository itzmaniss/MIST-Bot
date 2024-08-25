from datetime import timedelta, datetime
import logging
from mcstatus import JavaServer
import asyncio


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler("MCM.log")
file_handler.setLevel(logging.INFO)

#logging.basicConfig(filename="MCMlog", level=logging.INFO)
formatter = logging.Formatter('%(levelname)s: %(name)s: %(message)s')

file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

logger.info("Helper has been loaded")

def format_timedelta(delta):
    total_seconds = int(delta.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours}h {minutes}m {seconds}s"


def get_now() -> str:
    return datetime.now().time().strftime("%H:%M")


def players_online(server_name: str) -> bool:
    server_ip = {"ATM9": "brainrot.tntcraft.xyz", "Vanilla": "mc.tntcraft.xyz:25573"}

    server = JavaServer.lookup(server_ip[server_name])
    status = server.status()
        
    if status:
        logging.error(f"There are still {status.players.online} players online.")
        return status.players.online > 0

    return False



async def ping_server(server):
    response = 1
    while response != 0:
        process = await asyncio.create_subprocess_exec(
            "ping", "-c", "1", server,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        await process.wait()
        response = process.returncode
    return True


