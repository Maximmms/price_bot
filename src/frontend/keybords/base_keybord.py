from telebot.types import ReplyKeyboardMarkup, KeyboardButton

def get_main_keyboard():
    """
    Создаёт постоянную клавиатуру с кнопкой «Поиск» внизу.
    """
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False, row_width=1)
    keyboard.add(KeyboardButton("🔍 Поиск"))
    return keyboard