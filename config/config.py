import toml
import pathlib

class Config:
    # Load environment variables from config.toml
    _config = toml.load(pathlib.Path("./config/config.toml"))

    # Bot Configuration
    COMMAND_PREFIX = '%'
    
    # API Configuration
    API_URL = _config['instance']['api']['url']
    API_KEY = _config['instance']['api']['key']
    DISCORD_TOKEN = _config['discord']['token']
    
    # Features Configuration
    ALLOWED_USERS = _config["discord"]["allowed_users"]
    ALLOWED_CHANNELS = _config["discord"]["allowed_channels"]
    
    # Music Configuration
    MUSIC_CHANNEL_ID = _config["discord"]["music_channel_id"]
    MAX_SONG_DURATION = _config["discord"]["max_song_duration"]  # 10 minutes
    
    # Cooldowns (in seconds)
    START_COOLDOWN =  _config["discord"]["start_cooldown"]   # 1 hour
    COMMAND_COOLDOWN =  _config["discord"]["command_cooldown"]   # 3 seconds

    # Instance details
    UUID = {
        "vanilla": _config['instance']['uuid']['vanilla'],
        "ATM9": _config['instance']['uuid']['ATM9']
    }
    
    DAEMON_ID = {
        "vanilla": _config['instance']['daemon_id']['vanilla'],
        "ATM9": _config['instance']['daemon_id']['ATM9']
    }