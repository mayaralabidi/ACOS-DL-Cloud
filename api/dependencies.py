from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from .db import AsyncSessionLocal


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Provide an async SQLAlchemy session per request."""
    async with AsyncSessionLocal() as session:
        yield session