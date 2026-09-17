import requests
import json
from telebot.async_telebot import AsyncTeleBot
from telebot.types import Message
from frontend.tgbot.keyboards.base_keyboard import get_main_keyboard
from src.utils import bot_logger as logger
import os


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
        response = requests.get(f"{BACKEND_URL}/users/me", timeout=WEB_APP_DATA_TIMEOUT)
        response.raise_for_status()
        data = response.json()

        logger.info("Информация о пользователе успешно получена")
        await bot.send_message(
            chat_id=message.chat.id,
            text=f"Ваше имя: {data['username']}\nВаш email: {data['email']}",
            reply_markup=get_main_keyboard()
        )
    except requests.Timeout:
        logger.error("Таймаут при запросе к бэкенду")
        await bot.send_message(message.chat.id, "Сервер не ответил вовремя. Попробуйте позже.")
    except requests.RequestException as e:
        logger.error(f"Ошибка HTTP-запроса: {e}")
        await bot.send_message(message.chat.id, "Не удалось подключиться к серверу.")
    except KeyError as e:
        logger.error(f"Отсутствует ожидаемое поле в ответе: {e}")
        await bot.send_message(message.chat.id, "Получены некорректные данные от сервера.")
    except Exception as e:
        logger.exception(f"Неожиданная ошибка: {e}")
        await bot.send_message(message.chat.id, "Произошла внутренняя ошибка. Попробуйте позже.")


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


async def handle_web_app_data(message: Message, bot: AsyncTeleBot) -> None:
    """
    Обработчик данных из Web App.
    Парсит JSON с артикулом и списком партнёров, отправляет заглушку.
    """
    logger.info(f"Получены web_app_data от {message.from_user.id}: {message.web_app_data.data}")

    if not is_private_chat(message):
        await bot.send_message(
            message.from_user.id,
            "✅ Данные получены, но результат доступен только в личных сообщениях."
        )
        return

    try:
        # Парсим JSON из данных Web App
        data = json.loads(message.web_app_data.data)
        article = data.get("article", "").strip()
        partners = data.get("partners", [])

        if not article:
            await bot.send_message(
                message.chat.id,
                "❌ Артикул не указан. Пожалуйста, введите корректное значение.",
                reply_markup=get_main_keyboard()
            )
            return

        if not partners:
            await bot.send_message(
                message.chat.id,
                "❌ Не выбран ни один партнёр для поиска.",
                reply_markup=get_main_keyboard()
            )
            return

        # Формируем список выбранных магазинов
        partners_list = ", ".join(partners)
        if len(partners) > 3:
            partners_list = f"{partners[0]}, {partners[1]} и {len(partners) - 2} других"

        if len(partners) == 1:
            store_text = "Магазин"
        else:
            store_text = "Магазины"

        # Отправляем статус поиска
        await bot.send_message(
            chat_id=message.chat.id,
            text=(
                f"🔍 Артикул: <b>{article}</b> — получен.\n"
                f"🏪 {store_text}: {partners_list}\n"
                f"⏳ Ведётся поиск..."
            ),
            parse_mode="HTML",
            reply_markup=get_main_keyboard()
        )

        # Запрос к каждому поставщику
        for partner in partners:
            partner_key = partner.lower()
            logger.info(f"Отправлен запрос к бэкенду для партнёра {partner_key}, артикул {article}")

            try:
                response = requests.get(
                    f"{BACKEND_URL}/vendors/{partner_key}",
                    params={"article": article},
                    timeout=WEB_APP_DATA_TIMEOUT
                )
                response.raise_for_status()
                result = response.json()

                if not result:
                    await bot.send_message(
                        message.chat.id,
                        f"📦 <b>{partner}</b>:\n❌ Нет данных для артикула <code>{article}</code>.",
                        parse_mode="HTML"
                    )
                    continue

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

            except requests.Timeout:
                await bot.send_message(
                    message.chat.id,
                    f"⏰ Таймаут при запросе к <b>{partner}</b>.",
                    parse_mode="HTML"
                )
            except requests.HTTPError as e:
                if response.status_code == 404:
                    await bot.send_message(
                        message.chat.id,
                        f"❌ Поставщик <b>{partner}</b> не найден.",
                        parse_mode="HTML"
                    )
                else:
                    await bot.send_message(
                        message.chat.id,
                        f"❌ Ошибка {response.status_code} при запросе к <b>{partner}</b>.",
                        parse_mode="HTML"
                    )
            except requests.RequestException as e:
                logger.error(f"Ошибка сети при запросе к {partner}: {e}")
                await bot.send_message(
                    message.chat.id,
                    f"❌ Ошибка при запросе к <b>{partner}</b>.",
                    parse_mode="HTML"
                )
            except Exception as e:
                logger.exception(f"Неизвестная ошибка при обработке ответа от {partner}: {e}")
                await bot.send_message(
                    message.chat.id,
                    f"❌ Ошибка при обработке данных <b>{partner}</b>.",
                    parse_mode="HTML"
                )

    except json.JSONDecodeError as e:
        logger.error(f"Ошибка парсинга JSON из web_app_data: {e}")
        await bot.send_message(
            message.chat.id,
            "❌ Ошибка: неверный формат данных. Попробуйте снова.",
            reply_markup=get_main_keyboard()
        )
    except Exception as e:
        logger.exception(f"Неожиданная ошибка при обработке web_app_data: {e}")
        await bot.send_message(
            message.chat.id,
            "Произошла ошибка при обработке данных.",
            reply_markup=get_main_keyboard()
        )