import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    def __init__(self):
        self.BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
        if not self.BOT_TOKEN:
            raise ValueError("BOT_TOKEN не найден в переменных окружения. Убедитесь, что он задан.")


settings = Settings()