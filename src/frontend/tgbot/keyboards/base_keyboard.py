from telebot.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo

# Константа для URL Web App (вынесена для удобства и централизации)
WEB_APP_URL = "https://maximmms.github.io/price_bot/app.html"

def get_main_keyboard() -> ReplyKeyboardMarkup:
    """
    Возвращает клавиатуру с кнопкой, запускающей Web App.
    Отображается только в личных сообщениях.

    :return: ReplyKeyboardMarkup с кнопкой Web App
    """
    keyboard = ReplyKeyboardMarkup(
        resize_keyboard=True,           # Кнопки подстраиваются по размеру
        one_time_keyboard=False,        # Клавиатура остаётся после нажатия
        input_field_placeholder="Нажмите кнопку «🔍 Поиск артикула»"
    )
    keyboard.add(
        KeyboardButton(
            text="🔍 Поиск артикула",
            web_app=WebAppInfo(url=WEB_APP_URL)
        )
    )
    return keyboard