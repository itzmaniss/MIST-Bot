import logging


def setup_logging(name: str, log_file: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)

    formatter = logging.Formatter("%(levelname)s: %(name)s: %(message)s")
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    return logger
