"""Базовый абстрактный класс для API провайдеров."""

from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseVendorAPI(ABC):
    """Базовый класс для всех API провайдеров."""

    @abstractmethod
    async def search(self, article: str) -> Dict[str, Any]:
        """
        Поиск товара по артикулу.

        :param article: Артикул для поиска
        :return: Словарь с данными товара
        """
        ...
