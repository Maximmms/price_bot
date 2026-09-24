import asyncio
import io
import os
from datetime import datetime
from typing import List

from fastapi import APIRouter, Query, UploadFile, File, Form

from app.backend.services.vendors.netlab import NetlabAPI
from app.backend.db.schemas import VendorSearchRequest, VendorFileUploadRequest
from app.backend.db.dao import CatalogEntryDAO
from app.utils.logging_config import backend_logger as logger
from app.config.settings import settings

vendor_router = APIRouter(prefix="/vendors", tags=["Поставщики"])

# Маппинг имён поставщиков на ключи API
VENDOR_KEY_MAP = {
    "Netlab": "netlab",
    "Merlion": "merlion",
    "Treolan": "treolan",
    "OCS": "ocs",
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
    partner_key = VENDOR_KEY_MAP.get(partner, partner.lower())

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


@vendor_router.get("/ocs", description="Получить данные от поставщика OCS")
async def get_ocs(article: str = Query(..., description="Артикул для поиска у поставщика OCS")):
    pass


@vendor_router.get("/3logic", description="Получить данные от поставщика 3logic")
async def get_3logic(article: str = Query(..., description="Артикул для поиска у поставщика 3Logic")):
    pass


@vendor_router.get("/catalog/search", description="Поиск по загруженному каталогу")
async def search_catalog(part_number: str = Query(..., description="Артикул для поиска")):
    """Поиск товаров в загруженном каталоге."""
    logger.info(f"Поиск по каталогу: артикул={part_number}")

    try:
        entries = await CatalogEntryDAO.search_by_part_number(part_number)

        results = []
        for entry in entries:
            results.append({
                "id": entry.id,
                "part_number": entry.part_number,
                "sku_id": entry.sku_id,
            })

        return {
            "part_number": part_number,
            "count": len(results),
            "results": results
        }
    except Exception as e:
        logger.error(f"Ошибка при поиске по каталогу: {e}")
        return {
            "status": "error",
            "message": str(e)
        }


@vendor_router.post("/upload-pricelist", description="Загрузить прайс-лист")
async def upload_pricelist(
        file: UploadFile = File(...),
        partner: str = Form(...)
):
    """
    Загрузка прайс-листа поставщика.
    Поддерживаемые форматы: .xlsx, .xls, .csv
    Файл парсится и данные сохраняются в БД.
    """
    logger.info(f"Получен запрос на загрузку файла {file.filename} для поставщика {partner}")
    logger.info(f"Партнер: {partner}")

    if not file.filename:
        return {
            "status": "error",
            "message": "Не указан файл"
        }

    # Читаем файл
    file_content = await file.read()

    # Определяем формат и парсим
    entries = []
    filename_lower = file.filename.lower()

    try:
        if filename_lower.endswith(".csv"):
            import csv
            csv_file = io.StringIO(file_content.decode("utf-8"))
            reader = csv.DictReader(csv_file)
            for row in reader:
                entry = parse_csv_row(row)
                if entry:
                    entries.append(entry)
        elif filename_lower.endswith((".xlsx", ".xls")):
            try:
                import openpyxl
                wb = openpyxl.load_workbook(io.BytesIO(file_content), data_only=True)
                ws = wb.active
                header = None
                for row in ws.iter_rows(values_only=True):
                    if header is None:
                        header = [str(col).strip().lower().replace('\n', ' ') if col else "" for col in row]
                        logger.info(f"Заголовки файла: {header}")
                    else:
                        row_dict = dict(zip(header, row))
                        logger.debug(f"Строка: {row_dict}")
                        entry = parse_csv_row(row_dict)
                        if entry:
                            entries.append(entry)
                            logger.debug(f"Парсинг успешен: {entry}")
                        else:
                            logger.debug(f"Парсинг пропущен (part_number=None): {row_dict}")
            except ImportError:
                return {
                    "status": "error",
                    "message": "Для обработки Excel файлов установите openpyxl: pip install openpyxl"
                }
        else:
            return {
                "status": "error",
                "message": "Поддерживаемые форматы: .xlsx, .xls, .csv"
            }
    except Exception as e:
        logger.error(f"Ошибка при парсинге файла: {e}")
        return {
            "status": "error",
            "message": f"Ошибка при обработке файла: {str(e)}"
        }

    logger.info(f"Всего записей после парсинга: {len(entries)}")

    if not entries:
        return {
            "status": "success",
            "message": "Файл загружен, но записи не найдены",
            "inserted": 0,
            "skipped": 0,
            "total": 0
        }

    # Сохраняем в БД
    logger.info(f"Начало сохранения в БД: {len(entries)} записей...")
    try:
        result = await CatalogEntryDAO.bulk_insert(entries)
        logger.info(
            f"Успешно сохранено: {result['inserted']} вставлено, {result['skipped']} пропущено из {result['total']}"
        )
        return {
            "status": "success",
            "message": f"Прайс-лист {partner} успешно загружен",
            "partner": partner,
            "filename": file.filename,
            **result
        }
    except Exception as e:
        logger.error(f"Ошибка при сохранении в БД: {e}")
        return {
            "status": "error",
            "message": f"Ошибка при сохранении в БД: {str(e)}"
        }


def parse_csv_row(row: dict) -> dict:
    """
    Парсит одну строку CSV/Excel файла и возвращает словарь для БД.
    """
    part_number = None
    sku_id = ""

    # Номенклатурный номер -> sku_id
    for key in ["номенклатурный номер", "идентификатор товара у партнера", "идентификатор"]:
        if key in row and row[key]:
            sku_id = row[key]
            break

    # Каталожный номер -> part_number
    for key in ["каталожный номер", "part_number", "артикул", "артикул поставщика", "артикул ocs", "код", "article",
                "арт"]:
        if key in row and row[key]:
            part_number = row[key]
            break

    if not part_number:
        return None

    return {
        "part_number": part_number,
        "sku_id": sku_id,
    }
