from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from .config import get_settings

settings = get_settings()

engine_kwargs = {
    "echo": (settings.app_env == "dev"),
}
if not settings.database_url.startswith("sqlite"):
    engine_kwargs.update(
        {
            "pool_size": 10,
            "max_overflow": 20,
        }
    )

engine = create_async_engine(settings.database_url, **engine_kwargs)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """Declarative base for all ORM models."""
