import logging
import os
from datetime import datetime
from typing import Optional


class Logger:
    def __init__(self, name: str, log_dir: Optional[str] = None):
        self.logger = logging.getLogger(name)
        self.setup_logger(log_dir)

    def setup_logger(self, log_dir: Optional[str] = None):
        """Setup logging configuration"""
        try:
            if not log_dir:
                log_dir = os.path.join(os.path.expanduser("~"), ".ai_debug_assistant", "logs")
                os.makedirs(log_dir, exist_ok=True)

            log_file = os.path.join(log_dir, f"debug_assistant_{datetime.now().strftime('%Y%m%d')}.log")

            # Create formatter
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )

            # Create file handler
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)

            # Create console handler
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            console_handler.setFormatter(formatter)

            # Add handlers to logger
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)
            self.logger.setLevel(logging.DEBUG)

        except Exception as e:
            print(f"Error setting up logger: {e}")
            raise

    def debug(self, message: str):
        """Log debug message"""
        self.logger.debug(message)

    def info(self, message: str):
        """Log info message"""
        self.logger.info(message)

    def warning(self, message: str):
        """Log warning message"""
        self.logger.warning(message)

    def error(self, message: str):
        """Log error message"""
        self.logger.error(message)

    def critical(self, message: str):
        """Log critical message"""
        self.logger.critical(message)

    def exception(self, message: str):
        """Log exception message"""
        self.logger.exception(message)


def setup_logger(name: str, log_dir: Optional[str] = None) -> Logger:
    """Create and return a logger instance"""
    return Logger(name, log_dir)