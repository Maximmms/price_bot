import json
import os

import aiohttp

from telebot.async_telebot import AsyncTeleBot
from telebot.types import Message

from app.frontend.keyboards.main import get_main_keyboard
from app.utils.logging_config import bot_logger as logger
from app.utils.http_client import HTTPClient

# Загрузка URL бэкенда из переменных окружения
BACKEND_URL = os.getenv("BACKEND_URL")
WEB_APP_DATA_TIMEOUT = 10  # Таймаут для запросов к бэкенду


def is_private_chat(message: Message) -> bool:
    """
    Проверяет, является ли чат приватным.
    В группах и каналах использование Web App запрещено.

    :param message: Объект сообщения
    :return: True, если чат приватный
    """
    if message.chat.type != "private":
        logger.warning(f"Доступ запрещён: команда в неприватном чате ({message.chat.type}) от {message.from_user.id}")
        return False
    return True


async def send_welcome(bot: AsyncTeleBot, message: Message) -> None:
    """
    Обработчик команды /start.
    Отправляет приветственное сообщение с клавиатурой.
    """
    logger.info(f"Пользователь {message.from_user.id} вызвал /start")

    if not is_private_chat(message):
        await bot.send_message(
            message.chat.id,
            "Бот работает только в личных сообщениях. Напишите ему: @ваш_бот"
        )
        return

    text = f"Привет, {message.from_user.first_name}! Готов помочь с поиском."
    await bot.send_message(
        chat_id=message.chat.id,
        text=text,
        reply_markup=get_main_keyboard()
    )
