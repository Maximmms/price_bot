import asyncio

from telebot.async_telebot import AsyncTeleBot
from config import settings
from src.frontend.handlers.handlers_registry import register_handlers
from src.utils import bot_logger as logger


class Bot:
    def __init__(self):
        self.bot = AsyncTeleBot(settings.BOT_TOKEN)
        register_handlers(self.bot)

    def run(self):
        logger.info('Запуск бота...')
        asyncio.run(self.bot.polling())

if __name__ == '__main__':
    Bot().run()