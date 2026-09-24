from telebot.async_telebot import AsyncTeleBot
from app.frontend.handlers.start import send_welcome
from app.frontend.handlers.about import about_user
from app.frontend.handlers.search import ask_for_article, handle_article_text


def register_handlers(bot: AsyncTeleBot) -> None:
    """
    Регистрирует все обработчики команд и текстовых сообщений.

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

    # Обработчик текстового сообщения с артикулом
    @bot.message_handler(func=lambda m: m.text and len(m.text.strip()) > 0 and m.text.strip() != "🔍 Поиск артикула")
    async def article_handler(message):
        await handle_article_text(bot, message)
