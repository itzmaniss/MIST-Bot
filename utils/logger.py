import logging
from typing import Optional


class Logger:
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)

        file_handler = logging.FileHandler("bot.log")
        file_handler.setLevel(logging.INFO)
        formatter = logging.Formatter("%(levelname)s: %(name)s: %(message)s")
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

    def info(self, message: str) -> None:
        self.logger.info(message)

    def error(self, message: str) -> None:
        self.logger.error(message)
