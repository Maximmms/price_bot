import logging
from concurrent.futures import ThreadPoolExecutor
from logging.handlers import RotatingFileHandler
import os
from datetime import datetime

class AsyncFileHandler(RotatingFileHandler):
    """
    Асинхронный обработчик логов, использующий потоки для записи в файл.
    """

    def __init__(self, filename, maxBytes=0, backupCount=0, encoding=None, delay=False):
        super().__init__(filename, maxBytes=maxBytes, backupCount=backupCount, encoding=encoding, delay=delay)
        self.executor = ThreadPoolExecutor(max_workers=1)

    def emit(self, record):
        # Выполняем запись асинхронно в отдельном потоке
        self.executor.submit(super().emit, record)

    def close(self):
        self.executor.shutdown(wait=True)
        super().close()


class BotLogger:
    def __init__(self, name, log_level=logging.INFO, log_file=None, max_file_size=10*1024*1024, backup_count=5):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(log_level)

        if self.logger.handlers:
            return

        formatter = logging.Formatter(
            fmt="[%(asctime)s.%(msecs)03d] %(name)s | %(levelname)-7s | %(funcName)s:%(lineno)-3d | %(message)s",
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # Консольный обработчик
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        # Асинхронная запись в файл
        if log_file:
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
            file_handler = AsyncFileHandler(
                log_file,
                maxBytes=max_file_size,
                backupCount=backup_count,
                encoding='utf-8'
            )
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

    def log(self, message, level=logging.INFO):
        self.logger.log(level, message)

    def info(self, message):
        self.logger.info(message)

    def warning(self, message):
        self.logger.warning(message)

    def error(self, message):
        self.logger.error(message)

    def debug(self, message):
        self.logger.debug(message)

    def critical(self, message):
        self.logger.critical(message)

    def exception(self, message):
        self.logger.exception(message)