from app.utils.logging_config import backend_logger as logger


class OcsAPI:
    def __init__(self, token: str):
        self.token = token
        self.products = {}   #Словарь соответствия парт номеров и id товаров

        if not self.token:
            raise ValueError("Необходимо установить токен доступа")

    def upload_file(self, file: bytes):
        pass
