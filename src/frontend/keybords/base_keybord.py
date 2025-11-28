from telebot.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo

def get_main_keyboard():
    """
    Клавиатура с Web App через ngrok.
    """

    web_app_url = "https://myname.github.io/telegram-bot-shop/app.html"

    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False, row_width=1)
    keyboard.add(KeyboardButton("🔍 Поиск артикула", web_app=WebAppInfo(url=web_app_url)))
    return keyboard