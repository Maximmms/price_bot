"""Конфигурации провайдеров-заглушек для будущих реализаций."""

from typing import Dict, Any

# Заглушки для провайдеров, которые ещё не реализованы
VENDOR_STUBS = {
    "treolan": {
        "status": "not_implemented",
        "message": "Поиск по этому поставщику временно недоступен",
    },
    "merlion": {
        "status": "not_implemented",
        "message": "Поиск по этому поставщику временно недоступен",
    },
    "resurs": {
        "status": "not_implemented",
        "message": "Поиск по этому поставщику временно недоступен",
    },
    "3logic": {
        "status": "not_implemented",
        "message": "Поиск по этому поставщику временно недоступен",
    },
}


async def get_vendor_stub(vendor_key: str) -> Dict[str, Any]:
    """Возвращает заглушку для ненастроенного провайдера."""
    stub = VENDOR_STUBS.get(vendor_key)
    if stub:
        return {
            "partner": vendor_key,
            "status": "not_implemented",
            "error": stub["message"],
        }
    return {
        "partner": vendor_key,
        "status": "not_implemented",
        "error": "Поиск по этому поставщику временно недоступен",
    }
