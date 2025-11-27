from telebot.async_telebot import AsyncTeleBot
from config import settings
from src.frontend.keybords.base_keybord import get_main_keyboard
from src.utils import bot_logger as logger
import requests


async def send_welcome(bot: AsyncTeleBot, message):
    logger.info(f"Пользователь {message.from_user.id} вызвал команду /start")
    text = f"Привет, {message.from_user.first_name}! Я бот. Готов ответить на ваши вопросы."
    await bot.send_message(
        message.chat.id,
        text,
        reply_markup=get_main_keyboard(),
    )


async def about_user(bot: AsyncTeleBot, message):
    logger.info(f"Пользователь {message.from_user.id} запросил информацию о себе (/about)")
    try:
        response = requests.get("http://127.0.0.1:8000/users/me")
        response.raise_for_status()
        data = response.json()
        logger.info("Информация о пользователе успешно получена с сервера")
        await bot.send_message(
            message.chat.id,
            f"Ваше имя: {data['username']}\nВаш email: {data['email']}\n",
            reply_markup=get_main_keyboard()
        )
    except requests.RequestException as e:
        logger.error(f"Ошибка при запросе к серверу: {e}")
        await bot.send_message(message.chat.id, "Не удалось получить данные. Попробуйте позже.")
    except Exception as e:
        logger.exception(f"Неожиданная ошибка при обработке /about: {e}")
        await bot.send_message(message.chat.id, "Произошла внутренняя ошибка.")

async def ask_for_article(bot: AsyncTeleBot, message):
    logger.info(f"Пользователь {message.from_user.id} запросил артикул {message.text}")
    await bot.send_message(
        message.chat.id,
        "Введите артикул для поиска:",
        reply_markup=get_main_keyboard()  # Сохраняем кнопку
    )