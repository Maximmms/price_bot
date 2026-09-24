"""Заглушка для провайдера Merlion."""

from typing import Any, Dict

from app.backend.services.vendors.base import BaseVendorAPI


class MerlionAPI(BaseVendorAPI):
    async def search(self, article: str) -> Dict[str, Any]:
        return {
            "partner": "merlion",
            "status": "not_implemented",
            "error": "Поиск по этому поставщику временно недоступен",
        }
