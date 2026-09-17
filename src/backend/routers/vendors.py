import asyncio
import os
from typing import List

from fastapi import APIRouter, Query
from pydantic import BaseModel
from src.backend.services.vendors.netlab_api import NetlabAPI
from src.utils import backend_logger as logger

from config import settings

vendor_router = APIRouter(prefix="/vendors", tags=["Поставщики"])


class VendorSearchRequest(BaseModel):
    article: str
    partners: List[str]


# Маппинг имён поставщиков на ключи API
VENDOR_KEY_MAP = {
    "Netlab": "netlab",
    "Merlion": "merlion",
    "Treolan": "treolan",
    "OCS": "osc",
    "3Logic": "3logic",
}


@vendor_router.post("/search", description="Поиск по артикулу у нескольких поставщиков")
async def search_vendors(search_request: VendorSearchRequest):
    """
    Поиск товара у нескольких поставщиков параллельно.
    Принимает JSON: {"article": "XT902", "partners": ["Netlab", "Merlion"]}
    """
    logger.info(f"Получен запрос на поиск артикула {search_request.article} у поставщиков: {search_request.partners}")

    results = []

    # Запускаем задачи для каждого поставщика параллельно
    tasks = []
    for partner in search_request.partners:
        tasks.append(query_vendor(partner, search_request.article))

    gathered = await asyncio.gather(*tasks, return_exceptions=True)

    for i, partner in enumerate(search_request.partners):
        result = gathered[i]
        if isinstance(result, Exception):
            results.append({
                "partner": partner,
                "status": "error",
                "error": str(result)
            })
        else:
            results.append(result)

    return {
        "article": search_request.article,
        "results": results
    }


async def query_vendor(partner: str, article: str):
    """
    Запрос данных у одного поставщика.
    """
    partner_key = VENDOR_KEY_MAP.get(partner.lower(), partner.lower())

    if partner_key == "netlab":
        return await _query_netlab(partner, article)
    else:
        # Пока не реализовано для остальных поставщиков
        return {
            "partner": partner,
            "status": "not_implemented",
            "error": "Поиск по этому поставщику временно недоступен"
        }


async def _query_netlab(partner: str, article: str):
    """
    Запрос данных у Netlab.
    """
    try:
        logger.info(f"Запрос к Netlab: артикул {article}")
        nl = NetlabAPI(
            login=settings.netlab_config.get("login"),
            password=settings.netlab_config.get("password")
        )
        data = await nl.get_partnumber_sku(article)

        if not data:
            return {
                "partner": partner,
                "status": "success",
                "data": {}
            }

        return {
            "partner": partner,
            "status": "success",
            "data": data
        }
    except Exception as e:
        logger.error(f"Ошибка при запросе к Netlab: {e}")
        return {
            "partner": partner,
            "status": "error",
            "error": f"Ошибка при получении данных от {partner}"
        }


@vendor_router.get("/netlab", description="Получить данные от поставщика Netlab")
async def get_netlab(article: str = Query(..., description="Артикул для поиска у поставщика NetLab")):
    logger.info(f"Получен запрос на поиск артикула {article} у поставщика Netlab")
    nl = NetlabAPI(
        login=settings.netlab_config.get("login"),
        password=settings.netlab_config.get("password")
    )
    result = await nl.get_partnumber_sku(article)
    return result


@vendor_router.get("/merlion", description="Получить данные от поставщика Merlion")
async def get_merlion(article: str = Query(..., description="Артикул для поиска у поставщика Merlion")):
    pass


@vendor_router.get("/treolan", description="Получить данные от поставщика Treolan")
async def get_treolan(article: str = Query(..., description="Артикул для поиска у поставщика Treolan")):
    pass


@vendor_router.get("/osc", description="Получить данные от поставщика OSC")
async def get_osc(article: str = Query(..., description="Артикул для поиска у поставщика OSC")):
    pass


@vendor_router.get("/3logic", description="Получить данные от поставщика 3logic")
async def get_3logic(article: str = Query(..., description="Артикул для поиска у поставщика 3Logic")):
    pass
