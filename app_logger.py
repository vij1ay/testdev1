import logging
import sys
from datetime import datetime
from pathlib import Path
from logging.handlers import RotatingFileHandler
from enum import Enum

# Create logs directory if it doesn't exist
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

# Log file naming with timestamp
current_time = datetime.now().strftime("%Y-%m-%d")
LOG_FILE = LOG_DIR / f"app_{current_time}.log"

# Log format with more details
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s"
LOG_LEVEL = logging.DEBUG  # Changed from INFO to DEBUG to show all levels


class LogLevel(str, Enum):
    """Centralized log levels"""

    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    EXCEPTION = "exception"


class AppLogger:
    """
    Centralized logging handler for the application.
    Implements a singleton pattern to ensure consistent logging across the app.
    """

    _instance = None
    _logger = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AppLogger, cls).__new__(cls)
            cls._instance._initialize_logger()
        return cls._instance

    def _initialize_logger(self):
        """Initialize the root logger with file and console handlers"""
        if self._logger is None:
            self._logger = logging.getLogger("vj-app")
            self._logger.setLevel(LOG_LEVEL)

            # Remove any existing handlers to avoid duplicate logs
            self._logger.handlers = []

            # File Handler with rotation
            file_handler = RotatingFileHandler(
                LOG_FILE,
                maxBytes=10 * 1024 * 1024,  # 10MB
                backupCount=5,
                encoding="utf-8",
            )
            file_handler.setLevel(LOG_LEVEL)  # Set file handler to DEBUG level
            file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
            self._logger.addHandler(file_handler)

            # Console Handler
            log_console = False
            if log_console:
                console_handler = logging.StreamHandler(sys.stdout)
                console_handler.setLevel(
                    LOG_LEVEL
                )  # Set console handler to DEBUG level
                console_handler.setFormatter(logging.Formatter(LOG_FORMAT))
                self._logger.addHandler(console_handler)

            # Prevent propagation to root logger
            self._logger.propagate = False

    def log(self, level: LogLevel, message: str, **kwargs):
        """Traditional method support"""
        log_func = getattr(self._logger, level.value)
        if level in [LogLevel.ERROR, LogLevel.CRITICAL]:
            kwargs.setdefault("exc_info", True)
        log_func(message, **kwargs)


# Global logger instance
logger = AppLogger()._logger

def log_message(level: LogLevel, message: str, **kwargs):
    """Helper function to log messages using the global logger instance"""
    logger.log(level, message, **kwargs)