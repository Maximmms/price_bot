from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase, declared_attr

db_url = "sqlite+aiosqlite:///catalog.db"
engine = create_async_engine(db_url, echo=False)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


class Base(DeclarativeBase):
    __abstract__ = True

    @declared_attr.directive
    def __tablename__(self, cls) -> str:
        return cls.__name__.lower()


async def init_db():
    """Инициализация базы данных (создание таблиц, если не существуют)."""
    async with engine.begin() as conn:
        # Создаём таблицы только если их нет (без drop_all)
        await conn.run_sync(Base.metadata.create_all)
