"""
Async database session and engine; table creation on startup.
"""
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings
from app.db.base import Base
from app.db.models import User  # noqa: F401 - ensure models are registered

# Normalize DATABASE_URL for async drivers (SQLite/PostgreSQL/MySQL)
def _get_async_url() -> str:
    raw = get_settings().DATABASE_URL
    if raw.startswith("sqlite:///"):
        return raw.replace("sqlite:///", "sqlite+aiosqlite:///", 1)
    if raw.startswith("postgresql://"):
        return raw.replace("postgresql://", "postgresql+asyncpg://", 1)
    if raw.startswith("mysql://"):
        return raw.replace("mysql://", "mysql+aiomysql://", 1)
    return raw


engine = create_async_engine(
    _get_async_url(),
    echo=get_settings().DEBUG,
    future=True,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency that yields an async database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """Create all tables. Safe to call on every startup (idempotent for existing tables)."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
