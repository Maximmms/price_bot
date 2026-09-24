from typing import List, Optional

from fastapi import UploadFile, File
from pydantic import BaseModel, Field, ConfigDict


class CatalogItemBase(BaseModel):
    """Одна строка справочника."""
    part_number: str = Field(..., min_length=1, description="Каталожный номер (ключ поиска)")
    sku_id: str = Field(..., min_length=1, description="Номенклатурный номер поставщика")


class CatalogItem(CatalogItemBase):
    """Ответ API по одной строке."""
    model_config = ConfigDict(from_attributes=True)


class CatalogLookup(BaseModel):
    """Результат поиска по каталожному номеру."""
    part_number: str
    sku_id: str


class CatalogItemCreate(CatalogItemBase):
    pass


class CatalogBulkCreate(BaseModel):
    """Массовая загрузка."""
    items: List[CatalogItemCreate]


class ImportResult(BaseModel):
    inserted: int
    skipped: int
    total: int


class DuplicateGroup(BaseModel):
    cat: str
    count: int


class VendorFileUploadRequest(BaseModel):
    file: UploadFile = File(...)
    partner: str


class VendorSearchRequest(BaseModel):
    article: str
    partners: List[str]


class CatalogEntryResponse(BaseModel):
    """Ответ API для записи каталога."""
    model_config = ConfigDict(from_attributes=True)

    part_number: str
    sku_id: str


class CatalogSearchRequest(BaseModel):
    """Запрос поиска по каталогу."""
    part_number: str
