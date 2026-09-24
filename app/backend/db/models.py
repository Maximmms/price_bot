from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.backend.db.database import Base


class CatalogEntry(Base):
    """Запись прайс-листа поставщика."""
    __tablename__ = "catalog_entry"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    part_number: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    sku_id: Mapped[str] = mapped_column(String(255), default="")
