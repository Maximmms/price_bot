"""Заглушка для провайдера Resurs."""

from typing import Any, Dict

from app.backend.services.vendors.base import BaseVendorAPI


class ResursAPI(BaseVendorAPI):
    async def search(self, article: str) -> Dict[str, Any]:
        return {
            "partner": "resurs",
            "status": "not_implemented",
            "error": "Поиск по этому поставщику временно недоступен",
        }
