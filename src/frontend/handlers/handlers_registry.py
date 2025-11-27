from telebot.async_telebot import AsyncTeleBot
from src.frontend.handlers.base_handlers import ask_for_article, send_welcome, about_user


def register_handlers(bot: AsyncTeleBot):
    @bot.message_handler(commands=['start'])
    async def start_handler(message):
        await send_welcome(bot, message)

    @bot.message_handler(commands=['about'])
    async def about_handler(message):
        await about_user(bot, message)

    @bot.message_handler(func=lambda message: message.text == "🔍 Поиск")
    async def search_handler(message):
        await ask_for_article(bot, message)