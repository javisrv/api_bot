import logging
import os
import platform
import sys
from dotenv import load_dotenv

load_dotenv()
DEBUG = os.getenv('DEBUG')

# Define color codes for log levels
COLOR_CODES = {
    'DEBUG': '\033[94m',  # Blue
    'INFO': '\033[92m',   # Green
    'WARNING': '\033[93m',  # Yellow
    'ERROR': '\033[91m',   # Red
    'CRITICAL': '\033[95m'  # Magenta
}
RESET_CODE = '\033[0m'  # Reset color code


class ColoredFormatter(logging.Formatter):
    def format(self, record):
        levelname = record.levelname
        if levelname in COLOR_CODES:
            levelname_color = f"{COLOR_CODES[levelname]}{levelname}{RESET_CODE}"
            record.levelname = levelname_color
        return super().format(record)


class GetLogger:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG if DEBUG else logging.INFO)
        if not self.logger.handlers:
            # add console handler
            stream_handler = logging.StreamHandler(sys.stdout)
            try:
                hostname = os.uname().nodename
            except AttributeError:
                hostname = platform.uname().node
            except Exception:
                hostname = "unknown"
            formatter = ColoredFormatter(
                f'[%(asctime)s][%(levelname)s][{hostname}/%(process)d][%(module)s][%(funcName)s] %(message)s')
            stream_handler.setFormatter(formatter)
            self.logger.addHandler(stream_handler)


logger = GetLogger().logger