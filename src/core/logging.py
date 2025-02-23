import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

from src.core.config import settings



Path(settings.LOGS_DIR).mkdir(parents=True, exist_ok=True)
logger = logging.getLogger(settings.LOGGER_NAME)
logger.setLevel(level=settings.LOG_LEVEL)

fileHandler      = TimedRotatingFileHandler(filename=settings.LOG_FILE_PATH, 
                                            when='midnight',
                                            backupCount=30,
                                            encoding = 'utf-8')
logFileFormatter = logging.Formatter("%(asctime)s - %(levelname)s - %(filename)s:%(lineno)s - %(funcName)s() :: %(message)s")

fileHandler.setFormatter(logFileFormatter)
logger.addHandler(fileHandler)