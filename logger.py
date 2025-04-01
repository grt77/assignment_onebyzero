import logging
from config import Config
import os
from datetime import datetime

class Logger:
    def __init__(self, log_level=logging.INFO):
        self.logger = logging.getLogger("SimpleLogger")
        self.logger.setLevel(log_level)
        self.logfile=log_file_name=os.path.join(Config.LOG_FILE,"log_"+str(datetime.today().strftime('%Y-%m-%d')))

        if not self.logger.handlers:
            log_format = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

            file_handler = logging.FileHandler(self.logfile)
            file_handler.setLevel(log_level)
            file_handler.setFormatter(log_format)

            console_handler = logging.StreamHandler()
            console_handler.setLevel(log_level)
            console_handler.setFormatter(log_format)

            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)

    def debug(self, message):
        self.logger.debug(message)

    def info(self, message):
        self.logger.info(message)

    def warning(self, message):
        self.logger.warning(message)

    def error(self, message):
        self.logger.error(message)

    def critical(self, message):
        self.logger.critical(message)
