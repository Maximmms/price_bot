from telebot.async_telebot import AsyncTeleBot
from app.config.settings import settings
from app.frontend.handlers.registry import register_handlers
from app.utils.logging_config import bot_logger as logger


class Bot:
    def __init__(self):
        self.bot = AsyncTeleBot(settings.BOT_TOKEN)
        register_handlers(self.bot)

    def run(self):
        logger.info('Запуск бота...')
        import asyncio
        asyncio.run(self.bot.polling())


if __name__ == '__main__':
    Bot().run()
