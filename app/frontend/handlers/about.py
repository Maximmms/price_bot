import asyncio
import os

import aiohttp

from telebot.async_telebot import AsyncTeleBot
from telebot.types import Message

from app.frontend.keyboards.main import get_main_keyboard
from app.utils.logging_config import bot_logger as logger
from app.utils.http_client import HTTPClient


async def about_user(bot: AsyncTeleBot, message: Message) -> None:
    """
    Обработчик команды /about.
    Запрашивает информацию о пользователе с бэкенда и отображает её.
    """
    logger.info(f"Пользователь {message.from_user.id} запросил /about")

    if not is_private_chat(message):
        await bot.send_message(
            message.chat.id,
            "Команда /about доступна только в личных сообщениях."
        )
        return

    try:
        async with HTTPClient.get_session() as session:
            async with session.get(f"{BACKEND_URL}/users/me", timeout=WEB_APP_DATA_TIMEOUT) as response:
                response.raise_for_status()
                data = await response.json()

        logger.info("Информация о пользователе успешно получена")
        await bot.send_message(
            chat_id=message.chat.id,
            text=f"Ваше имя: {data['username']}\nВаш email: {data['email']}",
            reply_markup=get_main_keyboard()
        )
    except asyncio.TimeoutError:
        logger.error("Таймаут при запросе к бэкенду")
        await bot.send_message(message.chat.id, "Сервер не ответил вовремя. Попробуйте позже.")
    except aiohttp.ClientError as e:
        logger.error(f"Ошибка HTTP-запроса: {e}")
        await bot.send_message(message.chat.id, "Не удалось подключиться к серверу.")
    except KeyError as e:
        logger.error(f"Отсутствует ожидаемое поле в ответе: {e}")
        await bot.send_message(message.chat.id, "Получены некорректные данные от сервера.")
    except Exception as e:
        logger.exception(f"Неожиданная ошибка: {e}")
        await bot.send_message(message.chat.id, "Произошла внутренняя ошибка. Попробуйте позже.")


def is_private_chat(message: Message) -> bool:
    """Проверяет, является ли чат приватным."""
    if message.chat.type != "private":
        logger.warning(f"Доступ запрещён: команда в неприватном чате ({message.chat.type}) от {message.from_user.id}")
        return False
    return True


BACKEND_URL = os.getenv("BACKEND_URL")
WEB_APP_DATA_TIMEOUT = 10
