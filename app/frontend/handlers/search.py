import asyncio
import json
import os

import aiohttp

from telebot.async_telebot import AsyncTeleBot
from telebot.types import Message

from app.frontend.keyboards.main import get_main_keyboard
from app.utils.logging_config import bot_logger as logger


BACKEND_URL = os.getenv("BACKEND_URL")
WEB_APP_DATA_TIMEOUT = 10

# Словарь для хранения ожидающих ввода артикулов: user_id -> article
pending_articles = {}


def is_private_chat(message: Message) -> bool:
    """Проверяет, является ли чат приватным."""
    if message.chat.type != "private":
        logger.warning(f"Доступ запрещён: команда в неприватном чате ({message.chat.type}) от {message.from_user.id}")
        return False
    return True


async def ask_for_article(bot: AsyncTeleBot, message: Message) -> None:
    """
    Обработчик кнопки поиска. Запрашивает ввод артикула.
    """
    logger.info(f"Пользователь {message.from_user.id} запросил ввод артикула")

    if not is_private_chat(message):
        await bot.send_message(
            message.chat.id,
            "Поиск доступен только в личных сообщениях."
        )
        return

    await bot.send_message(
        chat_id=message.chat.id,
        text="Введите артикул для поиска:",
        reply_markup=get_main_keyboard()
    )


async def handle_article_text(bot: AsyncTeleBot, message: Message) -> None:
    """
    Обработчик текстового сообщения с артикулом.
    """
    article = message.text.strip()
    if not article:
        return

    logger.info(f"Пользователь {message.from_user.id} ввёл артикул: {article}")

    # Ищем по всем поставщикам
    partners = ["Netlab", "Merlion", "OCS", "3Logic", "Treolan"]

    await bot.send_message(
        chat_id=message.chat.id,
        text=f"🔍 Ищем артикул <b>{article}</b> у {len(partners)} поставщиков...",
        parse_mode="HTML",
        reply_markup=get_main_keyboard()
    )

    # Запрос к каждому поставщику параллельно
    tasks = []
    for partner in partners:
        tasks.append(fetch_vendor_data(partner, article, bot, message))

    await asyncio.gather(*tasks)


async def fetch_vendor_data(partner: str, article: str, bot: AsyncTeleBot, message: Message) -> None:
    """Запрос данных у одного поставщика."""
    partner_key = partner.lower()
    logger.info(f"Отправлен запрос к бэкенду для партнёра {partner_key}, артикул {article}")

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{BACKEND_URL}/api/v1/vendors/{partner_key}",
                params={"article": article},
                timeout=aiohttp.ClientTimeout(total=WEB_APP_DATA_TIMEOUT)
            ) as response:
                response.raise_for_status()
                result = await response.json()

        if not result:
            await bot.send_message(
                message.chat.id,
                f"📦 <b>{partner}</b>:\n❌ Нет данных для артикула <code>{article}</code>.",
                parse_mode="HTML",
                reply_markup=get_main_keyboard()
            )
            return

        # Красивый вывод для Netlab (и других, если структура похожа)
        name = result.get("Наименование", "Не указано")
        quantity = result.get("Количество", 0)
        transit = result.get("Транзиты", "Нет данных")
        remote = result.get("Удаленный склад", "Нет данных")
        price = result.get("Цена", "Не указана")

        # Форматируем цену и количество
        price_str = f"{float(price):,.2f} $" if isinstance(price, (int, float)) else price
        quantity_int = int(float(quantity)) if isinstance(quantity, (int, float)) else quantity

        message_text = (
            f"📦 <b>{partner}</b>\n"
            f"▫️ <b>Наименование:</b> {name}\n"
            f"▫️ <b>Артикул:</b> <code>{article}</code>\n"
            f"▫️ <b>Количество:</b> {quantity_int} шт\n"
            f"▫️ <b>Транзит:</b> {transit} шт\n"
            f"▫️ <b>Удалённый склад:</b> {remote}\n"
            f"▫️ <b>Цена:</b> <b>{price_str}</b>"
        )

        await bot.send_message(
            chat_id=message.chat.id,
            text=message_text,
            parse_mode="HTML",
            reply_markup=get_main_keyboard()
        )

    except asyncio.TimeoutError:
        await bot.send_message(
            message.chat.id,
            f"⏰ Таймаут при запросе к <b>{partner}</b>.",
            parse_mode="HTML",
            reply_markup=get_main_keyboard()
        )
    except aiohttp.ClientResponseError as e:
        if e.status == 404:
            await bot.send_message(
                message.chat.id,
                f"❌ Поставщик <b>{partner}</b> не найден.",
                parse_mode="HTML",
                reply_markup=get_main_keyboard()
            )
        else:
            await bot.send_message(
                message.chat.id,
                f"❌ Ошибка {e.status} при запросе к <b>{partner}</b>.",
                parse_mode="HTML",
                reply_markup=get_main_keyboard()
            )
    except aiohttp.ClientError as e:
        logger.error(f"Ошибка сети при запросе к {partner}: {e}")
        await bot.send_message(
            message.chat.id,
            f"❌ Ошибка при запросе к <b>{partner}</b>.",
            parse_mode="HTML",
            reply_markup=get_main_keyboard()
        )
    except Exception as e:
        logger.exception(f"Неизвестная ошибка при обработке ответа от {partner}: {e}")
        await bot.send_message(
            message.chat.id,
            f"❌ Ошибка при обработке данных <b>{partner}</b>.",
            parse_mode="HTML",
            reply_markup=get_main_keyboard()
        )
