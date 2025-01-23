from core.bot import DiscordBot
from features.minecraft import MinecraftFeature
from features.music import MusicFeature
from config.config import Config
from utils.logger import Logger

def main():
    # Setup logging
    logger = Logger("Discord Bot")
    logger.info('Starting bot...')
    
    # Initialize bot
    bot = DiscordBot()
    
    # Load features
    MinecraftFeature(bot)
    MusicFeature(bot)
    
    # Run bot
    logger.info('Bot initialized, starting...')
    bot.run_bot()

if __name__ == "__main__":
    main()
