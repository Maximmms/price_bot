import os
from typing import Dict, TypedDict

from dotenv import load_dotenv

load_dotenv()


class ProviderConfig(TypedDict):
    prefix: str
    required: list[str]
    optional: list[str]


class Settings:
    BOT_TOKEN: str
    BACKEND_URL: str
    AUTHORIZED_USERS: list[str]
    WEB_APP_URL: str

    # Netlab
    NETLAB_LOGIN: str
    NETLAB_PASSWORD: str
    NETLAB_AUTH_URL: str
    NETLAB_API_URL: str

    # Treolan
    TREOLAN_LOGIN: str
    TREOLAN_PASSWORD: str
    TREOLAN_AUTH_URL: str
    TREOLAN_API_URL: str

    # Resurs
    RESURSE_LOGIN: str
    RESURSE_PASSWORD: str

    # Merlion
    MERLION_CLIENT_CODE: str
    MERLION_LOGIN: str
    MERLION_PASSWORD: str

    # OCS
    OCS_TOKEN: str
    OCS_API_URL: str

    # Конфигурация поставщиков с обязательными полями
    PROVIDERS: Dict[str, ProviderConfig] = {
        "netlab": {
            "prefix": "NETLAB_",
            "required": ["LOGIN", "PASSWORD", "AUTH_URL", "API_URL"],
            "optional": [],
        },
        "treolan": {
            "prefix": "TREOLAN_",
            "required": ["LOGIN", "PASSWORD", "AUTH_URL", "API_URL"],
            "optional": [],
        },
        "resurs": {
            "prefix": "RESURSE_",
            "required": ["LOGIN", "PASSWORD"],
            "optional": [],
        },
        "merlion": {
            "prefix": "MERLION_",
            "required": ["CLIENT_CODE", "LOGIN", "PASSWORD"],
            "optional": [],
        },
        "ocs": {
            "prefix": "OCS_",
            "required": ["TOKEN", "API_URL"],
            "optional": [],
        },
    }

    def __init__(self):
        self.BOT_TOKEN: str = self._get_env("BOT_TOKEN", "")
        if not self.BOT_TOKEN:
            raise ValueError("BOT_TOKEN не найден в переменных окружения")

        self.BACKEND_URL: str = self._get_env("BACKEND_URL", "http://localhost:8000/api/v1")
        self.AUTHORIZED_USERS: list[str] = self._parse_authorized_users()
        self.WEB_APP_URL: str = self._get_env("WEB_APP_URL", "https://maximmms.github.io/price_bot/app.html")

        # Загрузка конфигураций провайдеров
        for provider_name, config in self.PROVIDERS.items():
            self._load_provider(config)

    @staticmethod
    def _get_env(key: str, default: str = "") -> str:
        """Получить переменную окружения."""
        return os.environ.get(key, default)

    def _parse_authorized_users(self) -> list[str]:
        """Парсинг списка авторизованных пользователей."""
        users_str = self._get_env("AUTHORIZED_USERS", "")
        return [user.strip() for user in users_str.split(",") if user.strip()]

    def _load_provider(self, config: ProviderConfig) -> None:
        """Загрузка переменных провайдера."""
        prefix = config["prefix"]

        # Загрузка обязательных полей
        for field in config["required"]:
            value = self._get_env(f"{prefix}{field}", "")
            setattr(self, f"{prefix.rstrip('_')}_{field}", value)

        # Загрузка опциональных полей
        for field in config["optional"]:
            value = self._get_env(f"{prefix}{field}", "")
            setattr(self, f"{prefix.rstrip('_')}_{field}", value)

    # Convenience methods для удобного доступа к данным поставщиков
    @property
    def netlab_config(self) -> Dict[str, str]:
        return {
            "login": self.NETLAB_LOGIN,
            "password": self.NETLAB_PASSWORD,
            "auth_url": self.NETLAB_AUTH_URL,
            "api_url": self.NETLAB_API_URL,
        }

    @property
    def treolan_config(self) -> Dict[str, str]:
        return {
            "login": self.TREOLAN_LOGIN,
            "password": self.TREOLAN_PASSWORD,
            "auth_url": self.TREOLAN_AUTH_URL,
            "api_url": self.TREOLAN_API_URL,
        }

    @property
    def resurs_config(self) -> Dict[str, str]:
        return {
            "login": self.RESURSE_LOGIN,
            "password": self.RESURSE_PASSWORD,
        }

    @property
    def merlion_config(self) -> Dict[str, str]:
        return {
            "client_code": self.MERLION_CLIENT_CODE,
            "login": self.MERLION_LOGIN,
            "password": self.MERLION_PASSWORD,
        }

    @property
    def ocs_config(self) -> Dict[str, str]:
        return {
            "token": self.OCS_TOKEN,
            "api_url": self.OCS_API_URL
        }


settings = Settings()
