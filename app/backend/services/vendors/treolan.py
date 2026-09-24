"""Заглушка для провайдера Treolan."""

from typing import Any, Dict

from app.backend.services.vendors.base import BaseVendorAPI


class TreolanAPI(BaseVendorAPI):
    async def search(self, article: str) -> Dict[str, Any]:
        return {
            "partner": "treolan",
            "status": "not_implemented",
            "error": "Поиск по этому поставщику временно недоступен",
        }
