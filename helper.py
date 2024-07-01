from datetime import timedelta, datetime
import logging
from mcstatus import JavaServer

logger = logging.getLogger("helper")
logging.basicConfig(filename="MCM.log", level=logging.INFO)


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
