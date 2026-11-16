from features.base import BotFeature
from config.config import Config
from utils.logger import Logger
from utils.helpers import discord_message


class HelpFeature(BotFeature):
    def __init__(self, bot):
        BotFeature.__init__(self, bot)
        self.ongoing_pings = {}
        self.logger = Logger("Smokers Bot")
        self.config = Config

    def setup_commands(self):
        @self.bot.hybrid_command(
            name="help", with_app_command=True, description="Shows all commands"
        )
        async def help(ctx):
            await discord_message(
                ctx,
                """```
### Minecraft Server Management

- `/start <server>`: Start a Minecraft server. Replace `<server>` with the name of the server (e.g., "vanilla", "ATM9").
- `/stop <server>`: Stop a Minecraft server.

### Music Playback

- `/join`: Join a voice channel.The bot will join the channel the user is currently in.
- `/play <query>`: Play a song from YouTube. `<query>` can be a search term or a YouTube URL.
- `/pause` or `/resume`: Pause or resume playback.
- `/skip`: Skip the currently playing song. 
- `/queue` or `/q`: Show the current song queue.
- `/clear`: Clear the song queue.
- `/remove <position>`: Remove a song from the queue at the specified position.
- `/volume <volume>` or `/vol <volume>`: Set the volume to a value between 0 and 100.
- `/loop`: Toggle loop mode on or off.
- `/np`, `/now`, or `/playing`: Show the currently playing song.
- `/seek <timestamp>`: Seek to a specific position in the current song. `<timestamp>` can be in the format "MM:SS" or a number of seconds.
- `/replay` or `/restart`: Replay the current song from the beginning.
- `/lyrics [song]` or `/ly [song]`: Fetch the lyrics for the specified song. If no song is specified, the lyrics for the currently playing song will be fetched.

### Smoking Feature

- `/wakey <user>`: "Wake up" a user by pinging them repeatedly. Only available to users with the "smoker" role and usable in designated channels.
- `/woken`: Stop the pinging for a user.The pinging for the user who used the command will be stopped.
                           ```""",
            )
