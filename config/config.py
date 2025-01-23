import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

class Config:
    # Bot Configuration
    COMMAND_PREFIX = '%'
    
    # API Configuration
    API_URL = "https://admin.tntcraft.xyz/api"
    API_KEY = os.getenv("api_key")
    DISCORD_TOKEN = os.getenv("discord_token")
    
    # Features Configuration
    ALLOWED_USERS = (304976615723499533, 476162085827379231)
    ALLOWED_CHANNELS = {
        "minecraft": "Vanilla",
        "atm9": "ATM9"
    }
    
    # Music Configuration
    MUSIC_CHANNEL_ID = int(os.getenv("music_channel_id", 0))
    MAX_SONG_DURATION = 600  # 10 minutes
    
    # Cooldowns (in seconds)
    START_COOLDOWN = 3600  # 1 hour
    COMMAND_COOLDOWN = 3  # 3 seconds

    #instance details
    UUID = {"minecraft": os.getenv("instance_id_vanilla"),
            "ATM9": os.getenv("instance_id_ATM9")}
    
    DAEMON_ID = {"minecraft": os.getenv("daemon_id_vanilla"),
            "ATM9": os.getenv("daemon_id_ATM9")}
