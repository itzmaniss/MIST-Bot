from abc import ABC, abstractmethod
from discord.ext import commands
import logging

class BotFeature(ABC):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.logger = logging.getLogger(self.__class__.__name__)
        self.setup_commands()
        self.logger.info(f'Feature {self.__class__.__name__} loaded')
    
    @abstractmethod
    def setup_commands(self) -> None:
        """Setup the feature's commands and event listeners."""
        pass
