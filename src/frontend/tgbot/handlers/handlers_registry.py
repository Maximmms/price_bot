from telebot.async_telebot import AsyncTeleBot
from frontend.tgbot.handlers.base_handlers import (
    send_welcome,
    about_user,
    ask_for_article,
    handle_web_app_data,
)


def register_handlers(bot: AsyncTeleBot) -> None:
    """
    Регистрирует все обработчики команд, текстовых сообщений и данных из Web App.

    :param bot: Экземпляр AsyncTeleBot
    """

    # Команда /start
    @bot.message_handler(commands=['start'])
    async def start_handler(message):
        await send_welcome(bot, message)

    # Команда /about
    @bot.message_handler(commands=['about'])
    async def about_handler(message):
        await about_user(bot, message)

    # Кнопка "🔍 Поиск артикула" (текстовое совпадение)
    @bot.message_handler(func=lambda m: m.text == "🔍 Поиск артикула")
    async def search_handler(message):
        await ask_for_article(bot, message)

    # Обработчик данных из Web App (единственный способ получить данные с интерфейса)
    bot.register_message_handler(
        handle_web_app_data,
        content_types=["web_app_data"],
        pass_bot=True
    )