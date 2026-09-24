from sqlalchemy import select, text
from sqlalchemy.exc import SQLAlchemyError

from app.backend.db.database import async_session_maker
from app.backend.db.models import CatalogEntry


class BaseDAO:
    model = None

    @classmethod
    async def find_one_id(cls, part_number: str):
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(part_number=part_number)
            result = await session.execute(query)
            return result.scalars().one_or_none()

    @classmethod
    async def add(cls, **values):
        async with async_session_maker() as session:
            async with session.begin():
                new_instance = cls.model(**values)
                session.add(new_instance)
                try:
                    await session.commit()
                except SQLAlchemyError as e:
                    await session.rollback()
                    raise e
                return new_instance


class CatalogEntryDAO(BaseDAO):
    model = CatalogEntry

    @classmethod
    async def add_entry(cls, part_number: str, sku_id: str = ""):
        """Добавить одну запись в каталог."""
        async with async_session_maker() as session:
            async with session.begin():
                existing = await cls.search_by_part_number(part_number)
                if existing:
                    existing[0].sku_id = sku_id or existing[0].sku_id
                    try:
                        await session.commit()
                    except SQLAlchemyError as e:
                        await session.rollback()
                        raise e
                    return existing[0]

                new_entry = cls.model(
                    part_number=part_number,
                    sku_id=sku_id,
                )
                session.add(new_entry)
                try:
                    await session.commit()
                except SQLAlchemyError as e:
                    await session.rollback()
                    raise e
                return new_entry

    @classmethod
    async def search_by_part_number(cls, part_number: str, partner: str = None):
        """Поиск записей по part_number."""
        async with async_session_maker() as session:
            query = select(cls.model).where(cls.model.part_number == part_number)
            result = await session.execute(query)
            return result.scalars().all()

    @classmethod
    async def bulk_insert(cls, entries: list):
        """Массовая вставка записей через INSERT OR REPLACE. Возвращает (inserted, skipped, total)."""
        total = len(entries)
        # INSERT OR REPLACE для SQLite — атомарный upsert
        sql = text(
            "INSERT OR REPLACE INTO catalog_entry (part_number, sku_id) VALUES (:part_number, :sku_id)"
        )

        async with async_session_maker() as session:
            try:
                await session.execute(sql, entries)
                await session.commit()
            except SQLAlchemyError as e:
                await session.rollback()
                raise e

        return {"inserted": total, "skipped": 0, "total": total}
