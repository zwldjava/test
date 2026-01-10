import logging
import sys
from pathlib import Path
from typing import Dict

from config.settings import config


class Logger:
    _instance = None
    _loggers: Dict[str, logging.Logger] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def get_logger(self, name: str = __name__) -> logging.Logger:
        if name in self._loggers:
            return self._loggers[name]

        logger = logging.getLogger(name)
        logger.setLevel(getattr(logging, config.get("logging.level", "INFO")))

        if not logger.handlers:
            console_formatter = logging.Formatter("%(message)s")
            file_formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )

            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(console_formatter)
            logger.addHandler(console_handler)

            log_file = config.get("logging.file")
            if log_file:
                log_path = Path(log_file)
                log_path.parent.mkdir(parents=True, exist_ok=True)
                file_handler = logging.FileHandler(log_file, encoding="utf-8")
                file_handler.setFormatter(file_formatter)
                logger.addHandler(file_handler)

        self._loggers[name] = logger
        return logger


def get_logger(name: str = __name__) -> logging.Logger:
    return Logger().get_logger(name)
