# Discord Bot

A modular Discord bot with Minecraft server management and music playback capabilities.

## Setup

1. Create and activate virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Copy .env.example to .env and fill in your credentials:
```bash
cp .env.example .env
```

4. Run the bot:
```bash
python main.py
```

## Project Structure

```
discord_bot/
├── config/         # Configuration settings
├── core/           # Core bot functionality
├── features/       # Bot features/commands
└── utils/          # Utility functions
```

## Adding New Features

1. Create a new file in the features directory
2. Create a class that inherits from BotFeature
3. Implement the setup_commands method
4. Import and initialize your feature in main.py
