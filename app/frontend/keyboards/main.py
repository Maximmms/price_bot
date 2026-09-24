from telebot.types import ReplyKeyboardMarkup, KeyboardButton


def get_main_keyboard() -> ReplyKeyboardMarkup:
    """
    Возвращает клавиатуру для Telegram бота.
    Только поиск артикула (без Web App).

    :return: ReplyKeyboardMarkup
    """
    keyboard = ReplyKeyboardMarkup(
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder="Выберите действие"
    )
    keyboard.add(
        KeyboardButton(text="🔍 Поиск артикула")
    )
    return keyboard
