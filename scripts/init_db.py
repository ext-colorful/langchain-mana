"""Initialize database tables."""

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import settings
from app.core.logging import logger
from app.infrastructure.database.models import Base


async def init_database():
    """Create all tables defined in models."""
    logger.info("Initializing database...")
    logger.info(f"Database URL: {settings.DATABASE_URL.split('@')[-1]}")

    engine = create_async_engine(settings.DATABASE_URL, echo=True)

    async with engine.begin() as conn:
        # Drop all tables (optional - comment out in production)
        # await conn.run_sync(Base.metadata.drop_all)

        # Create all tables
        await conn.run_sync(Base.metadata.create_all)

    await engine.dispose()
    logger.info("Database initialization complete!")


if __name__ == "__main__":
    asyncio.run(init_database())
