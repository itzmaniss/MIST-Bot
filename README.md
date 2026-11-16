# Discord Bot

This is a multi-purpose Discord bot built with Python and the discord.py library. It includes several features such as server management for Minecraft servers, music playback, and a smoking feature. 

## Table of Contents
- [Features](#features)
- [Installation](#installation)
  - [Prerequisites](#prerequisites)
  - [Setup](#setup)
- [Configuration](#configuration)
- [Usage](#usage)
  - [Minecraft Server Management](#minecraft-server-management)
  - [Music Playback](#music-playback) 
  - [Smoking Feature](#smoking-feature)
- [File Structure](#file-structure)
- [Contributing](#contributing)
- [License](#license)

## Features

- **Minecraft Server Management**: Start and stop Minecraft servers using the API of a server management panel. Includes safeguards to prevent abuse and ensure only authorized users can manage the servers.

- **Music Playback**: Play music in a voice channel using YouTube as the source. Supports queuing songs, skipping tracks, pausing/resuming, looping, and more. Also fetches lyrics for the currently playing song.

- **Smoking Feature**: A fun feature that allows users with a specific role to "wake up" other users by pinging them repeatedly. Includes checks to ensure it's used in the appropriate channels and by authorized users.

## Installation

### Prerequisites 

- Python 3.7+
- discord.py 
- yt-dlp
- aiohttp
- toml
- ffmpeg
- opus

### Setup

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/discord-bot.git
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Make sure FFMpeg, yt-dlp and opus are installed

4. Set up the necessary configuration files (see [Configuration](#configuration)).

5. Run the bot:
   ```
   python main.py
   ```

## Configuration

The bot's configuration is stored in a `config.toml` file. An example configuration file is provided in `config/config.toml`. You'll need to edit this file to include your bot token, server management API details, allowed users and channels, and more.

## Usage

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

## File Structure

- `main.py`: The main entry point of the bot.
- `config/`: Contains configuration files.
  - `config.py`: Loads the configuration from `config.toml` and provides it to the rest of the application.
  - `config.toml`: The main configuration file. 
- `core/`: Contains core functionality of the bot.
  - `bot.py`: Defines the main `DiscordBot` class.
  - `server_manager.py`: Handles interactions with the Minecraft server management API.
- `features/`: Contains the different features of the bot.
  - `base.py`: Defines a base `BotFeature` class that all features inherit from.
  - `minecraft.py`: Implements the Minecraft server management feature.
  - `music.py`: Implements the music playback feature.
  - `smoking.py`: Implements the smoking feature.
- `utils/`: Contains utility functions and classes. 
  - `helpers.py`: Various helper functions used throughout the bot.
  - `logger.py`: A simple logging utility.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the [MIT License](LICENSE).